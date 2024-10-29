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
	@LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$(shell pwd)/config/renovate-global-config.json" \
		renovate \
		--secrets '{"MY_SECRET": "my-secret"}' \
		--custom-env-variables '{"MY_VAR": "{{ secrets.MY_SECRET }}"}' \
		--token "$(GH_TOKEN)" "$(TEST_REPO)" \
		2>&1 >"$(BUILD_LOG_FILE)"


.PHONY: set-task-bundle
set-task-bundle:
	yq -i '(.spec.tasks[] | select(.name == "$(TASK_NAME)") | .taskRef.params[] | select(.name == "bundle") | .value) = "$(TASK_BUNDLE)"' ./pipelinerun.yaml


# Management of tasks and pipelines

.PHONY: build/and/push
build/and/push:
	./hack/build-and-push.sh

NEW_TASK_NAME ?= newtask
NEW_TASK_FILE = ./tasks/task-$(NEW_TASK_NAME)-0.1.yaml

.PHONY: add-new-task
add-new-task:
	cp ./tasks/task-init-0.1.yaml $(NEW_TASK_FILE)
	yq -i '.metadata.name = "$(NEW_TASK_NAME)"' $(NEW_TASK_FILE)
	yq -i '.spec.steps[0].name = "$(NEW_TASK_NAME)"' $(NEW_TASK_FILE)
	yq -i '.spec.tasks += {"name": "$(NEW_TASK_NAME)", "taskRef": {"name": "$(NEW_TASK_NAME)"}, "runAfter": ["init"]}' \
		./pipelines/pipeline-0.1.yaml
	git add $(NEW_TASK_FILE) ./pipelines/pipeline-0.1.yaml


LINE_LENGTH ?= 120
PY_SCRIPTS = migration-tool.py migrate.py utils.py migrate_per_task.py
PY_TESTS = test_migration_tool.py

.PHONY: code/format
code/format:
	@python3 -m black --line-length $(LINE_LENGTH) $(PY_SCRIPTS)

.PHONY: code/flake8
code/flake8:
	@python3 -m flake8 --max-line-length $(LINE_LENGTH) $(PY_SCRIPTS)

.PHONY: code/tests
code/tests:
	python3 -m pytest $(PY_TESTS)

.PHONY: code/check
code/check: code/format code/flake8 code/tests


.PHONY: utils/list-tasks
utils/list-tasks:
	yq '.spec.pipelineSpec.tasks[].name' pipelinerun.yaml | cat -n
	yq '.spec.tasks[].name' ./pipelines/pipeline-0.1.yaml | cat -n

.PHONY: utils/list-image-tag-digest-paires
utils/list-image-tag-digest-paires:
	curl -sL 'https://quay.io/api/v1/repository/$(IMAGE_REPO)/tag/?onlyActiveTags=true' | jq -r '.tags[] | (.name + " " + .manifest_digest)'

.PHONY: utils/clear-image-repos
utils/clear-image-repos:
	./hack/clear-image-repos.sh
