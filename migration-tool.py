#!/usr/bin/python3

import argparse
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from typing import Final
from urllib.request import urlopen

EXPECTED_IMAGE_NAMESPACE: Final = "konflux-ci/tekton-catalog"
DOCKER_BUILD_PL_BUNDLE_REPO: Final = "quay.io/konflux-ci/tekton-catalog/pipeline-docker-build"

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
    if image_repo.count("/") > 1:
        registry, repo = image_repo.split("/", 1)
    return ImageReference(registry=registry, repository=repo, tag=tag, digest=digest)


def find_pipeline(task_bundle: ImageReference) -> str:
    return ""


def main():
    parser = argparse.ArgumentParser(description="Konflux Pipeline Migration Tool")
    parser.add_argument("-f", "--from-task-bundle", required=True, metavar="PATH")
    parser.add_argument("-t", "--to-task-bundle", required=True, metavar="PATH")
    parser.add_argument("-l", "--log-file", metavar="PATH", default="run.log", help="Build log file. Defaults to %(default)s")

    args = parser.parse_args()

    build_log.addHandler(logging.FileHandler(args.log_file))

    build_log.info("Doing migration:")
    build_log.info("from: %s", args.from_task_bundle)
    build_log.info("to: %s", args.to_task_bundle)

    build_log.debug("inspect image: %s", args.to_task_bundle)
    image_ref = parse_image_reference(args.to_task_bundle)

    api_url = f"https://quay.io/api/v1/repository/{image_ref.repository}/manifest/{image_ref.digest}"
    with urlopen(api_url) as resp:
        data = json.loads(resp.read())
    build_log.debug("%s", json.dumps(data, indent=2))

    # find out the corresponding pipeline bundle

    api_url = f"https://quay.io/api/v1/repository/{image_ref.repository}/tag/"
    with urlopen(api_url) as resp:
        data = json.loads(resp.read())
    tag_regexp: Final = r"^[0-9.]+-[0-9a-f]+$"
    tag = [
        info for info in data["tags"]
        if info["manifest_digest"] == image_ref.digest and re.match(tag_regexp, info["name"])
    ]
    _, revision = tag[0]["name"].split("-")

    pipeline_bundle: Final = f"{DOCKER_BUILD_PL_BUNDLE_REPO}:{revision}"
    build_log.info("found pipeline bundle: %s", pipeline_bundle)


if __name__ == "__main__":
    main()
