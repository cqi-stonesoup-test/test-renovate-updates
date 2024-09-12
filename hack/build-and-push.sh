#!/usr/bin/env bash

set -u
set -e
set -o pipefail

pseudo_build=
show_pl_diff=
diff_output_file=

usage() {
    echo "$(basename "$0") [-p] [-d] [-o]"
    echo
    echo "Build task and pipeline bundles and push them to the registry. Run this script from the root of the repository."
    echo
    echo "  -p          pseudo build. No real task and pipeline bundles are built and pushed."
    echo "  -d          show differences between the last pipeline bundle and the newly built one."
    echo "  -o PATH     write the differences to this file."
    exit 1
}

while getopts ":phdo:" opt; do
    case $opt in
        d)
            show_pl_diff=true
            ;;
        o)
            diff_output_file=$OPTARG
            ;;
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
PIPELINES_BUILD_DIR="${PIPELINES_DIR}/build"

[ -e "$PIPELINES_BUILD_DIR" ] || mkdir "$PIPELINES_BUILD_DIR"

kustomize build -o "$PIPELINES_BUILD_DIR" ./pipelines/

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
        bundle_with_only_digest=$(grep "^Pushed Tekton Bundle to " <"$bundle_build_log" | cut -d' ' -f5)
        bundle_ref="${bundle}@${bundle_with_only_digest#*@}"
    fi

    git_resolver="{
\"resolver\": \"bundles\",
\"params\": [
    {\"name\": \"name\", \"value\": \"${task_name}\"},
    {\"name\": \"bundle\", \"value\": \"${bundle_ref}\"},
    {\"name\": \"kind\", \"value\": \"task\"}
]}"
    expr="(.spec.tasks[].taskRef | select(.name == \"${task_name}\")) |= ${git_resolver}"

    find "$PIPELINES_BUILD_DIR" -name "tekton.dev_v1_pipeline*.yaml" | \
    while read -r pipeline_file; do
        yq -i "$expr" "$pipeline_file"
    done
done

PIPELINE_BUNDLE_REPO_PREFIX=quay.io/mytestworkload/test-renovate-updates-pipeline-
declare -r PIPELINE_BUNDLE_REPO_PREFIX

GIT_REVISION=$(git rev-parse HEAD)
declare -r GIT_REVISION

fetch_last_pushed_pipeline_bundle() {
    local -r pipeline_name=${1?Missing pipeline name}
    return 0
}

# ###### Build and push pipeline bundles ######

find "$PIPELINES_BUILD_DIR" -name "tekton.dev_v1_pipeline*.yaml" | \
while read -r pipeline_file; do
    pipeline_name=$(yq '.metadata.name' "$pipeline_file")
    bundle_repo="${PIPELINE_BUNDLE_REPO_PREFIX}${pipeline_name}"

    if [ "$show_pl_diff" == "true" ]; then
        digest=$(
            curl -sL "https://quay.io/api/v1/repository/${bundle_repo#*/}/tag/?onlyActiveTags=true&limit=5" \
            | jq -r '.tags[0].manifest_digest'
        )
        latest_pushed_pipeline="/tmp/pipeline-${pipeline_name}-${digest#*:}.yaml"
        if [ ! -e "$latest_pushed_pipeline" ]; then
            tkn bundle list -o yaml "${bundle_repo}@${digest}" pipeline "$pipeline_name" >"$latest_pushed_pipeline"
        fi
    fi

    # echo
    $tkn_bundle_push -f "$pipeline_file" "${bundle_repo}:${GIT_REVISION}"

    if [ "$show_pl_diff" == "true" ]; then
        # FIXME: output format for multiple pipelines
        dyff between --omit-header --color=off --no-table-style "$latest_pushed_pipeline" "$pipeline_file" \
        | tee /tmp/pipeline-diff.txt
        python3 migrate_with_yq.py -i </tmp/pipeline-diff.txt | tee -a "$diff_output_file"
    fi
done
