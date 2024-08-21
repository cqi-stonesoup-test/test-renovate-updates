#!/usr/bin/env bash

echo "THIS IS FOR CHECKING FROM WHERE RENOVATE FINDS OUT THE EXECUTABLE FOR A POST-UPGRADE TASK."

plr_file=$1
[ -f "$plr_file" ] || exit

image_ref=$(yq '.spec.tasks[] | select(.name == "init") | .taskRef.params[] | select(.name == "bundle") | .value' "$plr_file")
digest=${image_ref#*@}
image_without_digest=${image_ref%@*}
image_repo=${image_without_digest%:*}
skopeo inspect "ocker://${image_repo}@${digest}"
