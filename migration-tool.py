#!/usr/bin/python3

import argparse
import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Final
from pathlib import Path
from urllib.request import urlopen
from collections.abc import Iterator

PIPELINE_BUNDLE_REPO: Final = "quay.io/mytestworkload/test-renovate-updates-pipeline"

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("migrate")

build_log = logging.getLogger("build.log")
build_log.setLevel(logging.DEBUG)


@dataclass
class PipelineEvent:
    bundle: str
    file_path: str


@dataclass
class ImageReference:
    registry: str
    repository: str
    tag: str
    digest: str

    @property
    def digest_pinned(self) -> str:
        return f"{self.registry}/{self.repository}@{self.digest}"

    @property
    def qualified_repository(self) -> str:
        return os.path.join(self.registry, self.repository)


def parse_image_reference(image_ref: str) -> ImageReference:
    if "@sha256" not in image_ref:
        raise ValueError(f"Image reference {image_ref} does not include digest.")
    image_without_digest, digest = image_ref.split("@")
    image_repo, tag = image_without_digest.rsplit(":", 1)
    registry = ""
    repo = image_repo
    if image_repo.count("/") > 1:
        registry, repo = image_repo.split("/", 1)
    return ImageReference(registry=registry, repository=repo, tag=tag, digest=digest)


# Example:  0.1-18a61693389c6c912df587f31bc3b4cc53eb0d5b
TASK_TAG_REGEXP: Final = r"^[0-9.]+-[0-9a-f]+$"


def find_pipeline(task_bundle: ImageReference) -> str:
    """Find pipeline that contains the given task bundle"""
    if not task_bundle.tag:
        raise ValueError(f"Tag is empty. Requiring a tag in form version-revision, e.g. 0.1-12345")
    _, revision = task_bundle.tag.rsplit("-", 1)
    return f"{PIPELINE_BUNDLE_REPO}:{revision}"


def fetch_pipeline_from_bundle(bundle_ref: str, dest_dir: str) -> str:
    pipeline_name: Final = "pipeline-build"
    cmd = ["tkn", "bundle", "list", "-o", "yaml", bundle_ref, "pipeline", pipeline_name]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    _, tag = bundle_ref.rsplit(":", 1)
    pipeline_file = Path(dest_dir, f"{pipeline_name}-{tag}.yaml")
    pipeline_file.write_text(proc.stdout, encoding="utf-8")
    return str(pipeline_file)


def analyze_pipeline() -> dict:
    return {}


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


def migrate_update(from_task_bundle: str, to_task_bundle: str, defs_temp_dir: str) -> None:
    events = pipeline_history(from_task_bundle, to_task_bundle, defs_temp_dir)
    history_len = len(events)
    if history_len < 2:
        return
    events.reverse()
    i = 1
    while i < history_len:
        prev_event = events[i-1]
        next_event = events[i]
        compare_cmd = ["dyff", "between", "--omit-header", "--no-table-style", prev_event.file_path, next_event.file_path]
        proc = subprocess.run(compare_cmd, check=True, capture_output=True, text=True)
        build_log.info(
            "changes from pipeline %s\n        to pipeline%s:\n%s",
            prev_event.bundle, next_event.bundle, proc.stdout,
        )
        i += 1


def main():
    parser = argparse.ArgumentParser(description="Konflux Pipeline Migration Tool")
    parser.add_argument("-f", "--from-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument("-t", "--to-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument("-l", "--log-file", metavar="PATH", default="run.log", help="Build log file. Defaults to %(default)s")

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

    migrate_update(args.from_task_bundle, args.to_task_bundle, defs_temp_dir)


if __name__ == "__main__":
    main()
