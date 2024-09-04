import json
import os.path
import re

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final
from urllib.request import urlopen

IMAGE_REGEX: Final = r"(?P<repository>[-0-9a-z._/]+)(:(?P<tag>[0-9a-z.-]+))?(@(?P<digest>sha256:[0-9a-f]{64}))?"

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
