import json
import os.path
import re

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Final
from urllib.request import urlopen

from ruamel.yaml import YAML

# Example:  0.1-18a61693389c6c912df587f31bc3b4cc53eb0d5b
TASK_TAG_REGEXP: Final = r"^[0-9.]+-[0-9a-f]+$"

IMAGE_REGEX: Final = r"(?P<repository>[-0-9a-z._/]+)(:(?P<tag>[0-9a-z.-]+))?(@(?P<digest>sha256:[0-9a-f]{64}))?"


def create_yaml_obj():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 8192
    return yaml


def load_yaml(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return create_yaml_obj().load(f)


def dump_yaml(filename: str, data: Any):
    with open(filename, "w", encoding="utf-8") as f:
        create_yaml_obj().dump(data, f)


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


def tkn_bundle_fetch(bundle_ref: ImageReference, output) -> None:
    manifest = quay_registry.get_manifest(bundle_ref.repository, bundle_ref.tag)
    fs_layers = manifest.get("fsLayers")
    if not fs_layers:
        raise ValueError("No layer data is included in manifest: %r", manifest)
    quay_registry.fetch_blob(bundle_ref.repository, fs_layers[0]["blobSum"], output)


def check_task_bundles_update_range():
    update_pairs: list[tuple[str, str, str]] = []
    with open("./task-bundles-updates.diff", "r") as f:
        from_task_bundle, to_task_bundle = "", ""
        for line in f:
            if line.startswith("-  "):
                _, from_task_bundle = line.rstrip().split(": ")
            elif line.startswith("+  "):
                _, to_task_bundle = line.rstrip().split(": ")
            if from_task_bundle and to_task_bundle:
                from_image_ref = parse_image_reference(from_task_bundle)
                to_image_ref = parse_image_reference(to_task_bundle)
                from_task_bundle_tag, to_task_bundle_tag = "", ""

                for tag in quay_list_repo_tags(from_image_ref.repository):
                    if re.match(TASK_TAG_REGEXP, tag["name"]) and tag["manifest_digest"] == from_image_ref.digest:
                        from_task_bundle_tag = tag["name"]
                        update_pairs.append(("R: " + from_task_bundle, tag["start_ts"], tag["name"]))
                    elif re.match(TASK_TAG_REGEXP, tag["name"]) and tag["manifest_digest"] == to_image_ref.digest:
                        to_task_bundle_tag = tag["name"]
                        update_pairs.append(("A: " + to_task_bundle, tag["start_ts"], tag["name"]))
                    if from_task_bundle_tag and to_task_bundle_tag:
                        break

                from_task_bundle, to_task_bundle = "", ""

    sorted_updates = sorted(update_pairs, key=lambda item: item[1], reverse=True)

    for _, _, tag_name in sorted_updates:
        print(tag_name.split("-")[1])


def determine_task_bundle_updates_range(from_task_bundle: str, to_task_bundle: str) -> list[dict]:
    from_bundle_ref = parse_image_reference(from_task_bundle)
    if not from_bundle_ref.digest:
        raise ValueError(f"Task bundle does not have digest: {from_task_bundle}")
    to_bundle_ref = parse_image_reference(to_task_bundle)
    if not to_bundle_ref.digest:
        raise ValueError(f"Task bundle does not have digest: {to_task_bundle}")

    r: list[dict] = []
    in_range = False
    task_tag_re = re.compile(TASK_TAG_REGEXP)

    for tag in quay_list_repo_tags(from_bundle_ref.repository):
        if not task_tag_re.match(tag["name"]):
            continue
        if tag["manifest_digest"] == to_bundle_ref.digest:
            r.append(tag)
            in_range = True
        elif tag["manifest_digest"] == from_bundle_ref.digest:
            r.append(tag)
            break
        elif in_range:
            r.append(tag)

    return r
