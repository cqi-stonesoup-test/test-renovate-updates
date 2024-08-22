#!/usr/bin/env bash

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
