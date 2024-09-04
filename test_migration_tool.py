import pytest
from utils import ImageReference, parse_image_reference


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
