#!/usr/bin/env bash

echo "THIS IS FOR CHECKING FROM WHERE RENOVATE FINDS OUT THE EXECUTABLE FOR A POST-UPGRADE TASK."

plr_file=$1
if [ ! -f "$plr_file" ]; then
    echo "PipelineRun file $plr_file does not exist." >&2
    exit 1
fi

image_ref=$(yq '.spec.tasks[] | select(.name == "init") | .taskRef.params[] | select(.name == "bundle") | .value' "$plr_file")
digest=${image_ref#*@}
image_without_digest=${image_ref%@*}
image_repo=${image_without_digest%:*}
echo "run: skopeo inspect docker://${image_repo}@${digest}"
skopeo inspect "docker://${image_repo}@${digest}"
