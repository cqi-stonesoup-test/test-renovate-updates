
import argparse
import json
import logging
import subprocess

from dataclasses import dataclass
from typing import Final

EXPECTED_IMAGE_NAMESPACE: Final = "konflux-ci/tekton-catalog"
DOCKER_BUILD_PL_BUNDLE_REPO: Final = "quay.io/konflux-ci/tekton-catalog/pipeline-docker-build"

build_log = logging.getLogger("build.log")
build_log.setLevel(logging.DEBUG)


@dataclass
class ImageReference:
    repository: str
    tag: str
    digest: str


def parse_image_reference(image_ref: str) -> ImageReference:
    if "@sha256" not in image_ref:
        raise ValueError(f"Image reference {image_ref} does not include digest.")
    image_without_digest, digest = image_ref.split("@")
    image_repo, tag = image_without_digest.rsplit(":", 1)
    return ImageReference(repository=image_repo, tag=tag, digest=digest)


def find_pipeline(task_bundle: ImageReference) -> str:
    return ""


def main():
    parser = argparse.ArgumentParser(description="Konflux Pipeline Migration Tool")
    parser.add_argument("-f", "--from-task-bundle")
    parser.add_argument("-t", "--to-task-bundle")
    parser.add_argument("-l", "--log-file", metavar="PATH", default="run.log", help="Build log file. Defaults to %(default)s")

    args = parser.parse_args()

    build_log.addHandler(logging.FileHandler(args.log_file))

    build_log.debug("Doing migration:")
    build_log.debug("from: %s", args.from_task_bundle)
    build_log.debug("to: %s", args.to_task_bundle)

    build_log.debug("inspect image: %s", args.to_task_bundle)
    proc = subprocess.run(
        ["skopeo", "inspect", "--no-tags", "docker://" + args.to_task_bundle],
        check=True, text=True, capture_output=True,
    )
    build_log.debug("%s", proc.stdout)

    from urllib.request import urlopen

    image_ref = parse_image_reference(args.to_task_bundle)
    api_url = f"https://quay.io//api/v1/repository/{image_ref.repository}/manifest/{image_ref.digest}"
    with urlopen(api_url) as resp:
        data = json.loads(resp.read())
    build_log.debug("%r", data)


if __name__ == "__main__":
    main()
