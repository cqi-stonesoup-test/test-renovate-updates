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
	podman push $(IMAGE) && \
	podman push $(FLOATING_IMAGE) && \
	skopeo inspect --format '{{ .Digest }}' "docker://$(FLOATING_IMAGE)"

.PHONY: clean/image/utils
clean/image/utils:
	for image_id in $$(podman images --format '{{.ID}}' $(REPO)); do \
		podman rmi "$$image_id"; \
		done

.PHONY: sleep-awhile
sleep-awhile:
	sleep 3


TEST_REPO ?= cqi-stonesoup-test/test-renovate-updates
BUILD_LOG_FILE ?= build.log

.PHONY: run/renovate
run/renovate:
	@echo "Renovating ..."
	@LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$(shell pwd)/renovate-global-config.json" \
		renovate --token "$(GH_TOKEN)" "$(TEST_REPO)" 2>&1 >"$(BUILD_LOG_FILE)"


.PHONY: set-task-bundle
set-task-bundle:
	yq -i '(.spec.tasks[] | select(.name == "$(TASK_NAME)") | .taskRef.params[] | select(.name == "bundle") | .value) = "$(TASK_BUNDLE)"' ./pipelinerun.yaml


# Management of tasks and pipelines

GIT_REVISION=$(shell git rev-parse HEAD)


.PHONY: build-and-push
build-and-push:
	./build-and-push.sh
