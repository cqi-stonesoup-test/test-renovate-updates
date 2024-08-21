VERSION ?= 0.1
TAG ?= $(VERSION)-$(shell git rev-parse HEAD)
REPO ?= quay.io/mytestworkload/test-renovate-updates-utils
IMAGE ?= $(REPO):$(TAG)
FLOATING_IMAGE = $(REPO):$(VERSION)

.PHONY: build/image/utils
build/image/utils:
	podman build -t $(IMAGE) -f Containerfile.utils --build-arg version=$(VERSION) . && \
	podman tag $(IMAGE) $(FLOATING_IMAGE)

.PHONY: push/image/utils
push/image/utils:
	podman push $(IMAGE) && podman push $(FLOATING_IMAGE)

.PHONY: clean/image/utils
clean/image/utils:
	for image_id in $$(podman images --format '{{.ID}}' $(REPO)); do \
		podman rmi "$$image_id"; \
		done

TEST_REPO ?= cqi-stonesoup-test/test-renovate-updates
BUILD_LOG_FILE ?= build.log

.PHONY: run/renovate
run/renovate:
	@LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$(shell pwd)/renovate-global-config.json" \
		renovate --token "$(GH_TOKEN)" "$(TEST_REPO)" 2>&1 >"$(BUILD_LOG_FILE)"
