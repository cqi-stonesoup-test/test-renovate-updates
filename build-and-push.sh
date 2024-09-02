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
	echo "tkn bundle push " "$@"
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

find ./definitions/ -maxdepth 1 -name "task-*.yaml" | while read -r file_path; do
    task_yaml_file="$(basename "$file_path")"
    task_name=$(echo "$task_yaml_file" | cut -d'-' -f2)
    task_version=$(echo "$task_yaml_file" | cut -d'-' -f3)
    task_version=${task_version%.*}  # remove the file extension

    bundle="quay.io/mytestworkload/test-renovate-updates-task-${task_name}:${task_version}"
    git_revision=$(git log -n 1 --pretty=format:%H -- "$file_path")

    if digest=$(skopeo inspect --no-tags --format='{{.Digest}}' "docker://${bundle}-${git_revision}" 2>/dev/null); then
	bundle_ref="${bundle}@${digest}"
    else
	digest_file="./definitions/temp/task-${task_name}-bundle-digest"
	tkn_bundle_push -f "./definitions/task-${task_name}-${task_version}.yaml" "${bundle}-${git_revision}"
	skopeo copy --digestfile "${digest_file}" "docker://${bundle}-${git_revision}" "docker://${bundle}"
	bundle_ref="${bundle}@$(cat "${digest_file}")"
    fi

    # digest_file="./definitions/temp/task-${task_name}-bundle-digest"
    # tkn_bundle_push -f "./definitions/task-${task_name}-${task_version}.yaml" "${bundle}-${git_revision}"
    # skopeo copy --digestfile "${digest_file}" "docker://${bundle}-${git_revision}" "docker://${bundle}"
    # bundle_ref="${bundle}@$(cat "${digest_file}")"

    git_resolver="{\"resolver\": \"bundles\", \"params\": [{\"name\": \"name\", \"value\": \"${task_name}\"}, {\"name\": \"bundle\", \"value\": \"${bundle_ref}\"}, {\"name\": \"kind\", \"value\": \"task\"}]}"
    yq -i "(.spec.tasks[].taskRef | select(.name == \"${task_name}\")) |= ${git_resolver}" ./definitions/temp/pipeline.yaml
done

PIPELINE_IMAGE_REPO=quay.io/mytestworkload/test-renovate-updates-pipeline
declare -r PIPELINE_IMAGE_REPO

git_revision=$(git log -n 1 --pretty=format:%H -- ./definitions/pipeline-0.1.yaml)
pipeline_bundle="${PIPELINE_IMAGE_REPO}:${git_revision}"
if ! skopeo inspect --no-tags --format '{{.Digest}}' "docker://${pipeline_bundle}" >/dev/null 2>&1
then
    echo
    tkn_bundle_push -f ./definitions/temp/pipeline.yaml "${pipeline_bundle}"
fi
