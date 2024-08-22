#!/usr/bin/env bash

set -o pipefail

plr_file=$1
if [ ! -f "$plr_file" ]; then
    echo "PipelineRun file $plr_file does not exist." >&2
    exit 1
fi

from_image_ref=$2
to_image_ref=$3

echo "

Doing migration:
from: $from_image_ref
to:   $to_image_ref

" >>README.md

digest=${to_image_ref#*@}
image_without_digest=${to_image_ref%@*}
image_repo=${image_without_digest%:*}
echo "inspect image: $to_image_ref"
echo "inspect image: $to_image_ref" >>README.md
skopeo inspect --no-tags "docker://${image_repo}@${digest}" >>README.md

expected_image_repo=quay.io/konflux-ci/tekton-catalog/task-summary

if [ "$image_repo" != "$expected_image_repo" ]; then
    echo "Skip handling image from $image_repo"
    exit 0
fi

tag=$(
    curl -s "https://quay.io/api/v1/repository/${image_repo}/tag/" | \
    jq -r ".tags[] | select(.manifest_digest == \"${digest}\") | select(.name | test(\"^[0-9.]+-[0-9a-f]+$\")) | .name"
)
revision=${tag#*-}

pl_bundle_ref="quay.io/konflux-ci/tekton-catalog/pipeline-docker-build:${revision}"
echo
echo "inspect pipeline bundle: $pl_bundle_ref"
skopeo inspect --no-tags "docker://${pl_bundle_ref}"
