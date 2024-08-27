#!/usr/bin/env bash

set -u
set -e
set -o pipefail

tkn_bundle_push() {
    local status
    local retry=0
    local -r interval=${RETRY_INTERVAL:-5}
    local -r max_retries=5
    while true; do
        tkn bundle push "$@" && break
        status=$?
        ((retry+=1))
        if [ $retry -gt $max_retries ]; then
            return $status
        fi
        echo "Waiting for a while, then retry the tkn bundle push ..."
        sleep "$interval"
    done
}

[ -e "./definitions/temp" ] || mkdir ./definitions/temp
cp ./definitions/pipeline-0.1.yaml ./definitions/temp/pipeline.yaml
git_revision=$(git rev-parse HEAD)

task_name=init
bundle="quay.io/mytestworkload/test-renovate-updates-task-${task_name}:0.1"
tkn_bundle_push -f "./definitions/task-${task_name}-0.1.yaml" "${bundle}-${git_revision}"
skopeo copy --digestfile ./definitions/temp/task-${task_name}-bundle-digest "docker://${bundle}-${git_revision}" "docker://${bundle}"
bundle_ref="${bundle}@$(cat ./definitions/temp/task-bundle-digest)"
git_resolver="{\"resolver\": \"bundles\", \"params\": [{\"name\": \"name\", \"value\": \"${task_name}\"}, {\"name\": \"bundle\", \"value\": \"${bundle_ref}\"}, {\"name\": \"kind\", \"value\": \"task\"}]}"
yq -i "(.spec.tasks[].taskRef | select(.name == \"${task_name}\")) |= ${git_resolver}" ./definitions/temp/pipeline.yaml

task_name=clone
bundle="quay.io/mytestworkload/test-renovate-updates-task-${task_name}:0.1"
tkn_bundle_push -f "./definitions/task-${task_name}-0.1.yaml" "${bundle}-${git_revision}"
skopeo copy --digestfile "./definitions/temp/task-${task_name}-bundle-digest" "docker://${bundle}-${git_revision}" "docker://${bundle}"
bundle_ref="${bundle}@$(cat ./definitions/temp/task-bundle-digest)"
git_resolver="{\"resolver\": \"bundles\", \"params\": [{\"name\": \"name\", \"value\": \"${task_name}\"}, {\"name\": \"bundle\", \"value\": \"${bundle_ref}\"}, {\"name\": \"kind\", \"value\": \"task\"}]}"
yq -i "(.spec.tasks[].taskRef | select(.name == \"${task_name}\")) |= ${git_resolver}" ./definitions/temp/pipeline.yaml

task_name=test
bundle="quay.io/mytestworkload/test-renovate-updates-task-${task_name}:0.1"
tkn_bundle_push -f "./definitions/task-${task_name}-0.1.yaml" "${bundle}-${git_revision}"
skopeo copy --digestfile "./definitions/temp/task-${task_name}-bundle-digest" "docker://${bundle}-${git_revision}" "docker://${bundle}"
bundle_ref="${bundle}@$(cat ./definitions/temp/task-bundle-digest)"
git_resolver="{\"resolver\": \"bundles\", \"params\": [{\"name\": \"name\", \"value\": \"${task_name}\"}, {\"name\": \"bundle\", \"value\": \"${bundle_ref}\"}, {\"name\": \"kind\", \"value\": \"task\"}]}"
yq -i "(.spec.tasks[].taskRef | select(.name == \"${task_name}\")) |= ${git_resolver}" ./definitions/temp/pipeline.yaml


tkn_bundle_push -f ./definitions/temp/pipeline.yaml "quay.io/mytestworkload/test-renovate-updates-pipeline:${git_revision}"
