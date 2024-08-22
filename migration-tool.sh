#!/usr/bin/env bash

set -e
set -u
set -o pipefail

declare -r EXPECTED_IMAGE_NAMESPACE=konflux-ci/tekton-catalog

declare -r from_image_ref=$1
declare -r to_image_ref=$2
declare -r output_file=${3:-run.log}

echo "

Doing migration:
from: $from_image_ref
to:   $to_image_ref

" >>"$output_file"

digest=${to_image_ref#*@}
image_without_digest=${to_image_ref%@*}
image_repo=${image_without_digest%:*}
echo "inspect image: $to_image_ref" | tee -a "$output_file"
skopeo inspect --no-tags "docker://${image_repo}@${digest}" >>"$output_file"

image_repo_without_registry="${image_repo#*/}"  # remove registry host
image_namespace="${image_repo_without_registry%/*}"  # remove image repo name
if [ "${image_namespace}" != "$EXPECTED_IMAGE_NAMESPACE" ]; then
    echo "Skip handling image from $image_repo"
    exit 0
fi

tag=$(
    curl -s "https://quay.io/api/v1/repository/${image_repo_without_registry}/tag/" | \
    jq -r ".tags[] | select(.manifest_digest == \"${digest}\") | select(.name | test(\"^[0-9.]+-[0-9a-f]+$\")) | .name"
)
revision=${tag#*-}

pl_bundle_ref="quay.io/konflux-ci/tekton-catalog/pipeline-docker-build:${revision}"
echo
echo "inspect pipeline bundle: $pl_bundle_ref" | tee -a "$output_file"
skopeo inspect --no-tags "docker://${pl_bundle_ref}" >>"$output_file"
