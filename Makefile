VERSION ?= 0.1
TAG ?= $(VERSION)-$(shell git rev-parse HEAD)
REPO ?= quay.io/mytestworkload/test-renovate-updates-utils
IMAGE ?= $(REPO):$(TAG)
FLOATING_IMAGE = $(REPO):$(VERSION)

BUILD_ROOT = /tmp/test-renovate-updates-xdg-data-home

.PHONY: build/image/utils
build/image/utils:
	XDG_DATA_HOME=$(BUILD_ROOT) \
	podman build -t $(IMAGE) -f Containerfile.utils --build-arg version=$(VERSION) . && \
	XDG_DATA_HOME=$(BUILD_ROOT) \
	podman tag $(IMAGE) $(FLOATING_IMAGE)

.PHONY: push/image/utils
push/image/utils:
	XDG_DATA_HOME=$(BUILD_ROOT) podman push $(IMAGE) && \
	XDG_DATA_HOME=$(BUILD_ROOT) podman push $(FLOATING_IMAGE)

