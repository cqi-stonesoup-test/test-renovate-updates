#!/usr/bin/env bash

set -euo pipefail

for_task=${1:?Missing task name}
task_file="./tasks/task-${for_task}-0.1.yaml"

if [ ! -e "$task_file" ]; then
    echo "Task file ${task_file} does not exist." >&2
    exit 1
fi

k8s_version=$(yq '.metadata.labels."app.kubernetes.io/version"' "$task_file")

# bump version
IFS=. read -r major minor patch_ <<<"$k8s_version"
if [ -z "$patch_" ]; then
    patch_=1
else
    ((++patch_))
fi
bumped_version="${major}.${minor}.${patch_}"

yq -i ".metadata.labels.\"app.kubernetes.io/version\" |= \"${bumped_version}\"" "$task_file"

cat >"tasks/migrations/task-${for_task}-${bumped_version}.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
pipeline=\$1
task_name=${for_task}

# Place migration steps here
EOF
