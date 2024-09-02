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

.PHONY: build/and/push
build/and/push:
	./build-and-push.sh

NEW_TASK_NAME ?= newtask
NEW_TASK_FILE = ./definitions/task-$(NEW_TASK_NAME)-0.1.yaml

.PHONY: add-new-task
add-new-task:
	cp ./definitions/task-clone-0.1.yaml $(NEW_TASK_FILE)
	yq -i '.metadata.name = "$(NEW_TASK_NAME)"' $(NEW_TASK_FILE)
	yq -i '.spec.steps[0].name = "$(NEW_TASK_NAME)"' $(NEW_TASK_FILE)
	yq -i '.spec.tasks += {"name": "$(NEW_TASK_NAME)", "taskRef": {"name": "$(NEW_TASK_NAME)"}, "runAfter": ["init"]}' ./definitions/pipeline-0.1.yaml


LINE_LENGTH ?= 120
PY_SCRIPTS = migration-tool.py migrate.py

.PHONY: code/format
code/format:
	@python3 -m black --line-length $(LINE_LENGTH) $(PY_SCRIPTS)

.PHONY: code/flake8
code/flake8:
	@python3 -m flake8 --max-line-length $(LINE_LENGTH) $(PY_SCRIPTS)

.PHONY: code/tests
code/tests:
	python3 -m pytest $(PY_SCRIPTS)

.PHONY: code/check
code/check: code/format code/flake8 code/tests
