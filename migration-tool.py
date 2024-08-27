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

PL_BUNDLE_REPO: Final = "quay.io/mytestworkload/test-renovate-updates-pipeline"

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("migrate")

build_log = logging.getLogger("build.log")
build_log.setLevel(logging.DEBUG)


@dataclass
class ImageReference:
    registry: str
    repository: str
    tag: str
    digest: str

    @property
    def digest_pinned(self) -> str:
        return f"{self.registry}/{self.repository}@{self.digest}"


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


TAG_REGEXP: Final = r"^[0-9.]+-[0-9a-f]+$"


def find_pipeline(task_bundle: ImageReference) -> str:
    api_url = f"https://quay.io/api/v1/repository/{task_bundle.repository}/tag/"
    with urlopen(api_url) as resp:
        data = json.loads(resp.read())
    tag = [
        info for info in data["tags"]
        if info["manifest_digest"] == task_bundle.digest and re.match(TAG_REGEXP, info["name"])
    ]
    _, revision = tag[0]["name"].split("-")

    return f"{PL_BUNDLE_REPO}:{revision}"


def download_pipeline_from_bundle(bundle_ref: str, dest_dir: str) -> str:
    pipeline_name: Final = "pipeline-build"
    cmd = ["tkn", "bundle", "list", "-o", "yaml", bundle_ref, "pipeline", pipeline_name]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    _, tag = bundle_ref.rsplit(":", 1)
    pipeline_file = Path(dest_dir, f"{pipeline_name}-{tag}.yaml")
    pipeline_file.write_text(proc.stdout, encoding="utf-8")
    return str(pipeline_file)


def main():
    parser = argparse.ArgumentParser(description="Konflux Pipeline Migration Tool")
    parser.add_argument("-f", "--from-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument("-t", "--to-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument("-l", "--log-file", metavar="PATH", default="run.log", help="Build log file. Defaults to %(default)s")

    args = parser.parse_args()

    build_log.addHandler(logging.FileHandler(args.log_file))

    build_log.info("Doing migration:")
    build_log.info("from: %s", args.from_task_bundle)
    build_log.info("to: %s", args.to_task_bundle)

    build_log.debug("inspect image: %s", args.to_task_bundle)

    # find out the corresponding pipeline bundle

    defs_temp_dir = os.path.join(os.getcwd(), "definitions", "temp")
    if not os.path.exists(defs_temp_dir):
        os.makedirs(os.path.join("definitions", "temp"))

    from_task_bundle_ref = parse_image_reference(args.from_task_bundle)
    from_pipeline_bundle: Final = find_pipeline(from_task_bundle_ref)
    build_log.info("found pipeline bundle: %s", from_pipeline_bundle)
    from_pipeline_file = download_pipeline_from_bundle(from_pipeline_bundle, defs_temp_dir)

    to_task_bundle_ref = parse_image_reference(args.to_task_bundle)
    to_pipeline_bundle: Final = find_pipeline(to_task_bundle_ref)
    build_log.info("found pipeline bundle: %s", to_pipeline_bundle)
    to_pipeline_file = download_pipeline_from_bundle(to_pipeline_bundle, defs_temp_dir)

    compare_cmd = ["dyff", "between", "--omit-header", "--no-table-style", from_pipeline_file, to_pipeline_file]
    proc = subprocess.run(compare_cmd, check=True, capture_output=True, text=True)
    build_log.info("changes to pipeline:\n%s", proc.stdout)


if __name__ == "__main__":
    main()
