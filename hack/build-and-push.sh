#!/usr/bin/env bash

set -u
set -e
set -o pipefail

pseudo_build=

usage() {
    echo "$(basename "$0") [-p]"
    echo
    echo "Build task and pipeline bundles and push them to the registry. Run this script from the root of the repository."
    echo
    echo "  -p      pseudo build. No real task and pipeline bundles are built and pushed."
    exit 1
}

while getopts ":ph" opt; do
    case $opt in
        p)
            pseudo_build=true
            ;;
        h)
            usage
            ;;
        *)
            usage
            ;;
    esac
done

_tkn_bundle_push() {
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

pseudo_tkn_bundle_push() {
    local task_file=
    local image_ref=
    while [ $# -gt 0 ]; do
        if [ "$1" == "-f" ]; then
            shift
            task_file=$1
        else
            part="${1%%/*}"
            if [ "$part" == "quay.io" ]; then
                image_ref=$1
            fi
        fi
        shift
    done
    if [ -z "$task_file" ]; then
        echo "Missing Tekton resource YAML file." 1>&2
        return 1
    fi
    if [ -z "$image_ref" ]; then
        echo "Missing Tekton bundle image reference." 1>&2
        return 1
    fi
    resource_kind=$(yq '.kind' "$task_file")
    resource_name=$(yq '.metadata.name' "$task_file")
    resource_image_repo="${image_ref%:*}"
    checksum=$(sha256sum "$task_file")
    checksum=${checksum%% *}
    echo "\
Creating Tekton Bundle:
- Added ${resource_kind}: ${resource_name} to image

Pushed Tekton Bundle to ${resource_image_repo}@sha256:${checksum}
"
}

if [ "$pseudo_build" == "true" ]; then
    tkn_bundle_push="pseudo_tkn_bundle_push"
else
    tkn_bundle_push="_tkn_bundle_push"
fi

# Extract tekton bundle reference from tkn-bundle-push output
extract_bundle_ref() {
    echo "^Pushed Tekton Bundle to " | cut -d' ' -f5
}

inspect_bundle_digest() {
    local -r image_ref=${1:?Missing image reference of a tekton bundle}
    if [ "$pseudo_build" == "true" ]; then
        return 1  # meaning the bundle does not exist in the registry yet.
    fi
    skopeo inspect --no-tags --format='{{.Digest}}' "docker://${image_ref}" 2>/dev/null
    return $?
}

TASKS_DIR=./tasks
PIPELINES_DIR=./pipelines
PIPELINES_BUILD_DIR="${PIPELINES_DIR}/temp"

[ -e "$PIPELINES_BUILD_DIR" ] || mkdir "$PIPELINES_BUILD_DIR"
cp "${PIPELINES_DIR}/pipeline-0.1.yaml" "${PIPELINES_BUILD_DIR}/pipeline.yaml"

find "$TASKS_DIR" -maxdepth 1 -name "task-*.yaml" | while read -r file_path; do
    task_yaml_file="$(basename "$file_path")"
    task_name=$(echo "$task_yaml_file" | cut -d'-' -f2)
    task_version=$(echo "$task_yaml_file" | cut -d'-' -f3)
    task_version=${task_version%.*}  # remove the file extension

    bundle="quay.io/mytestworkload/test-renovate-updates-task-${task_name}:${task_version}"
    git_revision=$(git log -n 1 --pretty=format:%H -- "$file_path")

    if digest=$(inspect_bundle_digest "${bundle}-${git_revision}"); then
        bundle_ref="${bundle}@${digest}"
    else
        task_filename="${TASKS_DIR}/task-${task_name}-${task_version}.yaml"
        k8s_task_version=$(yq '.metadata.labels."app.kubernetes.io/version"' "$task_filename")
        bundle_build_log=/tmp/bundle-build.log
        $tkn_bundle_push -f "${task_filename}" "${bundle}-${git_revision}" --label version="$k8s_task_version" | \
            tee "$bundle_build_log"
        if [ -z "$pseudo_build" ]; then
            skopeo copy "docker://${bundle}-${git_revision}" "docker://${bundle}"
        fi
        image_digest=$(extract_bundle_ref <"$bundle_build_log")
        bundle_ref="${bundle}@${image_digest}"
    fi

    git_resolver="{\"resolver\": \"bundles\", \"params\": [{\"name\": \"name\", \"value\": \"${task_name}\"}, {\"name\": \"bundle\", \"value\": \"${bundle_ref}\"}, {\"name\": \"kind\", \"value\": \"task\"}]}"
    yq -i "(.spec.tasks[].taskRef | select(.name == \"${task_name}\")) |= ${git_resolver}" "${PIPELINES_BUILD_DIR}/pipeline.yaml"
done

PIPELINE_IMAGE_REPO=quay.io/mytestworkload/test-renovate-updates-pipeline
declare -r PIPELINE_IMAGE_REPO

digest=$(curl -sL "https://quay.io/api/v1/repository/${PIPELINE_IMAGE_REPO#*/}/tag/?onlyActiveTags=true&limit=5" | jq -r '.tags[0].manifest_digest')
latest_pushed_pipeline="/tmp/pipeline-build-${digest#*:}.yaml"
if [ ! -e "$latest_pushed_pipeline" ]; then
    tkn bundle list -o yaml "${PIPELINE_IMAGE_REPO}@${digest}" pipeline pipeline-build >"$latest_pushed_pipeline"
fi

git_revision=$(git log -n 1 --pretty=format:%H -- "${PIPELINES_DIR}/pipeline-0.1.yaml")
pipeline_bundle="${PIPELINE_IMAGE_REPO}:${git_revision}"
if [ "$pseudo_build" == "true" ] || ! skopeo inspect --no-tags --format '{{.Digest}}' "docker://${pipeline_bundle}" >/dev/null 2>&1
then
    echo
    $tkn_bundle_push -f "${PIPELINES_BUILD_DIR}/pipeline.yaml" "${pipeline_bundle}"
fi

dyff between --omit-header --color=off --no-table-style "$latest_pushed_pipeline" "${PIPELINES_BUILD_DIR}/pipeline.yaml" | \
tee /tmp/pipeline-diff.txt
python3 migrate_with_yq.py -i </tmp/pipeline-diff.txt
