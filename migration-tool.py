#!/usr/bin/python3

import argparse
import json
import logging
import os
import pytest
import re
import tempfile
import tarfile
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from urllib.request import urlopen

import migrate

PIPELINE_BUNDLE_REPO: Final = "quay.io/mytestworkload/test-renovate-updates-pipeline"

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("migrate")

build_log = logging.getLogger("build.log")
build_log.setLevel(logging.DEBUG)


# Example:  0.1-18a61693389c6c912df587f31bc3b4cc53eb0d5b
TASK_TAG_REGEXP: Final = r"^[0-9.]+-[0-9a-f]+$"


@dataclass
class PipelineEvent:
    bundle: str
    file_path: str


@dataclass
class ImageReference:
    registry: str = ""
    repository: str = ""
    tag: str = ""
    digest: str = ""

    @property
    def digest_pinned(self) -> str:
        return f"{self.registry}/{self.repository}@{self.digest}"

    @property
    def qualified_repository(self) -> str:
        return os.path.join(self.registry, self.repository)


IMAGE_REGEX: Final = r"(?P<repository>[-0-9a-z._/]+)(:(?P<tag>[0-9a-z.-]+))?(@(?P<digest>sha256:[0-9a-f]{64}))?"


def parse_image_reference(image: str) -> ImageReference:
    registry, repository, tag, digest = "", "", "", ""
    match = re.match(IMAGE_REGEX, image)
    if match:
        repository = match.group("repository")
        tag = match.group("tag") or ""
        digest = match.group("digest") or ""
        parts = repository.split("/")
        if len(parts) > 1 and "." in parts[0]:
            registry = parts[0]
            repository = "/".join(parts[1:])
    return ImageReference(registry=registry, repository=repository, tag=tag, digest=digest)


def find_pipeline(task_bundle: ImageReference) -> str:
    """Find pipeline that contains the given task bundle"""
    if not task_bundle.tag:
        raise ValueError("Tag is empty. Requiring a tag in form version-revision, e.g. 0.1-12345")
    _, revision = task_bundle.tag.rsplit("-", 1)
    return f"{PIPELINE_BUNDLE_REPO}:{revision}"


class Registry:
    """Represents an image registry"""

    def __init__(self, host: str) -> None:
        self.host = host.rstrip("/")

    def get_manifest(self, repository: str, reference: str) -> dict:
        url: Final = f"{self.host}/v2/{repository}/manifests/{reference}"
        with urlopen(url) as resp:
            return json.load(resp)

    def fetch_blob(self, repository: str, digest: str, output) -> None:
        if not digest.startswith("sha256:"):
            raise ValueError("digest does not have prefix 'sha256:'")
        url: Final = f"{self.host}/v2/{repository}/blobs/{digest}"
        with urlopen(url) as resp:
            data = resp.read()
        output.write(data)


class QuayIO(Registry):

    def get_tag(self, repository: str, name: str) -> dict | None:
        tags = self.list_repo_tags(repository, name)
        if tags:
            return tags[0]
        return None

    def list_repo_tags(self, repository: str, specific_tag: str = "") -> list[dict]:
        tags: list[dict] = []
        page = 1
        while True:
            url = f"{self.host}/api/v1/repository/{repository}/tag/?page={page}&onlyActiveTags=true"
            if specific_tag:
                url += "&specificTag=" + specific_tag
            with urlopen(url) as resp:
                data = json.loads(resp.read())
            for tag in data["tags"]:
                tags.append(tag)
            if not data.get("has_additional"):
                break
            page = int(data["page"]) + 1
        return tags


quay_registry: Final = QuayIO("https://quay.io/")


def tkn_bundle_fetch(bundle_ref: ImageReference, output) -> None:
    manifest = quay_registry.get_manifest(bundle_ref.repository, bundle_ref.tag)
    fslayers = manifest.get("fsLayers")
    if not fslayers:
        raise ValueError("No layer data is included in manifest: %r", manifest)
    quay_registry.fetch_blob(bundle_ref.repository, fslayers[0]["blobSum"], output)


def fetch_pipeline_from_bundle(bundle: str, dest_dir: str) -> str:
    pipeline_name: Final = "pipeline-build"
    image_ref = parse_image_reference(bundle)
    pipeline_file = Path(dest_dir, f"{pipeline_name}-{image_ref.tag}.yaml")
    fd, temp_blob_file = tempfile.mkstemp()
    os.close(fd)
    try:
        with open(temp_blob_file, "wb") as f:
            tkn_bundle_fetch(image_ref, f)
        with tarfile.open(temp_blob_file, "r") as tar:
            members = tar.getmembers()
            if len(members) > 1:
                raise ValueError(f"Multiple members in pipeline bundle {bundle}")
            pl_content = tar.extractfile(members[0]).read().decode("utf-8")
            pipeline_file.write_text(pl_content)
    finally:
        os.unlink(temp_blob_file)
    return str(pipeline_file)


def map_task_bundle_to_pipeline_bundle(task_bundle: str) -> str:
    """Map task bundle to pipeline bundle which includes the task"""
    image_ref: Final = parse_image_reference(task_bundle)
    pipeline_bundle: Final = find_pipeline(image_ref)
    build_log.info("found pipeline bundle: %s", pipeline_bundle)
    return pipeline_bundle


def quay_list_repo_tags(repository: str) -> Iterator[dict]:
    page = 1
    while True:
        url = f"https://quay.io/api/v1/repository/{repository}/tag/?page={page}&onlyActiveTags=true"
        with urlopen(url) as resp:
            data = json.loads(resp.read())
        for tag in data["tags"]:
            yield tag
        if not data.get("has_additional"):
            break
        page = int(data["page"]) + 1


def task_update_history(from_task_bundle: str, to_task_bundle: str) -> list[ImageReference]:
    """Generate task bundle history from the newest to the oldest one"""
    task_bundles_history: list[ImageReference] = []
    append = task_bundles_history.append
    from_image_ref = parse_image_reference(from_task_bundle)
    to_image_ref = parse_image_reference(to_task_bundle)
    in_range = False
    for tag in quay_list_repo_tags(from_image_ref.repository):
        if not re.match(TASK_TAG_REGEXP, tag["name"]):
            continue
        if tag["manifest_digest"] == to_image_ref.digest:
            append(
                ImageReference(
                    registry=to_image_ref.registry,
                    repository=to_image_ref.repository,
                    tag=tag["name"],
                    digest=to_image_ref.digest,
                ),
            )
            in_range = True
        elif tag["manifest_digest"] == from_image_ref.digest:
            append(
                ImageReference(
                    registry=from_image_ref.registry,
                    repository=from_image_ref.repository,
                    tag=tag["name"],
                    digest=from_image_ref.digest,
                )
            )
            break
        elif in_range:
            append(
                ImageReference(
                    registry=from_image_ref.registry,
                    repository=from_image_ref.repository,
                    tag=tag["name"],
                    digest=tag["manifest_digest"],
                ),
            )
    return task_bundles_history


def pipeline_history(from_task_bundle: str, to_task_bundle: str, store_dir: str) -> list[PipelineEvent]:
    """Generate pipeline history from the newest to the oldest one"""
    task_bundles_history = task_update_history(from_task_bundle, to_task_bundle)
    history: list[PipelineEvent] = []
    for task_bundle in task_bundles_history:
        logger.debug("find pipeline for task bundle: %s", task_bundle)
        pipeline_bundle = find_pipeline(task_bundle)
        pipeline_file = fetch_pipeline_from_bundle(pipeline_bundle, store_dir)
        logger.debug("task bundle %s is included in pipelne %s", task_bundle, pipeline_file)
        history.append(PipelineEvent(bundle=pipeline_bundle, file_path=pipeline_file))
    return history


def compare_pipelines(from_pipeline: str, to_pipeline: str) -> str:
    """Compare two pipelines"""
    compare_cmd = [
        "dyff",
        "between",
        "--omit-header",
        "--detect-kubernetes",
        "--no-table-style",
        from_pipeline,
        to_pipeline,
    ]
    proc = subprocess.run(compare_cmd, check=True, capture_output=True, text=True)
    return proc.stdout


def migrate_update(from_task_bundle: str, to_task_bundle: str, defs_temp_dir: str, pipeline_run_file: str = "") -> None:
    # FIXME: all supported pipelines must be handled.
    #
    # Currently, there is no way to know which supported pipeline is based on,
    # unless the oci-ta pipelines because of task name has suffix -oci-ta.
    #
    # So, the process would be:
    # 1. fetch update history for each supported pipeline, e.g. docker-build, docker-build-oci-ta
    # 2. select the pipeline if it includes the current updated task
    events = pipeline_history(from_task_bundle, to_task_bundle, defs_temp_dir)

    history_len = len(events)
    if history_len < 2:
        return
    events.reverse()  # FIXME: call builtin reverse function instead
    i = 1
    while i < history_len:
        prev_event = events[i - 1]
        next_event = events[i]
        diff = compare_pipelines(prev_event.file_path, next_event.file_path)
        build_log.info("changes from pipeline %s to pipeline%s:\n%s", prev_event.bundle, next_event.bundle, diff)
        if pipeline_run_file:
            migrate.migrate_with_dsl(migrate.generate_dsl(migrate.convert_difference(diff)), pipeline_run_file)
        i += 1


def main():
    parser = argparse.ArgumentParser(description="Konflux Pipeline Migration Tool")
    parser.add_argument("-f", "--from-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument("-t", "--to-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument(
        "-l", "--log-file", metavar="PATH", default="run.log", help="Build log file. Defaults to %(default)s"
    )
    parser.add_argument(
        "-p",
        "--pipeline-run",
        metavar="PATH",
        dest="pipeline_run_file",
        default="",
        help="Update pipeline for this PipelineRun.",
    )

    args = parser.parse_args()

    from_task_bundle = args.from_task_bundle
    to_task_bundle = args.to_task_bundle

    if from_task_bundle == to_task_bundle:
        logger.info("same task bundles are specified.")
        return

    from_ref = parse_image_reference(from_task_bundle)
    to_ref = parse_image_reference(to_task_bundle)

    if from_ref.qualified_repository != to_ref.qualified_repository:
        logger.error("Given task bundles are not same image.")
        return

    build_log.addHandler(logging.FileHandler(args.log_file))

    build_log.info("Doing migration for task update:")
    build_log.info("from: %s", args.from_task_bundle)
    build_log.info("to: %s", args.to_task_bundle)

    build_log.debug("inspect image: %s", args.to_task_bundle)

    # find out the corresponding pipeline bundle

    defs_temp_dir = os.path.join(os.getcwd(), "definitions", "temp")
    if not os.path.exists(defs_temp_dir):
        os.makedirs(os.path.join("definitions", "temp"))

    migrate_update(args.from_task_bundle, args.to_task_bundle, defs_temp_dir, args.pipeline_run_file)


# ############## Tests #########################


@pytest.mark.parametrize(
    "image,expected",
    [
        ["konflux-ci/app", ImageReference(registry="", repository="konflux-ci/app", tag="", digest="")],
        ["quay.io/ns/app", ImageReference(registry="quay.io", repository="ns/app", tag="", digest="")],
        ["quay.io/ns/app:0.1", ImageReference(registry="quay.io", repository="ns/app", tag="0.1", digest="")],
        [
            "quay.io/ns/app:0.1@sha256:1f5e3c9aa72e321e53af20192c7a94f5a519840f3f3578ea04c8bcb104be8e9c",
            ImageReference(
                registry="quay.io",
                repository="ns/app",
                tag="0.1",
                digest="sha256:1f5e3c9aa72e321e53af20192c7a94f5a519840f3f3578ea04c8bcb104be8e9c",
            ),
        ],
        [
            "quay.io/ns/app@sha256:1f5e3c9aa72e321e53af20192c7a94f5a519840f3f3578ea04c8bcb104be8e9c",
            ImageReference(
                registry="quay.io",
                repository="ns/app",
                tag="",
                digest="sha256:1f5e3c9aa72e321e53af20192c7a94f5a519840f3f3578ea04c8bcb104be8e9c",
            ),
        ],
    ],
)
def test_parse_image_reference(image, expected):
    assert expected == parse_image_reference(image)


if __name__ == "__main__":
    main()
