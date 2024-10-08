#!/usr/bin/env bash
set -euo pipefail
pipeline=$1
task_name=coverage

remove_item_from_array() {
    local -r remove_item=$1
    local -r target_file=$2
    task_names=$(yq '.spec | .tasks[] | select(.name == "coverage") | .runAfter[]' "$target_file" | nl -v 0)
    grep "$remove_item" <<<"$task_names" | while read -r idx task_name; do
        yq -i "del(.spec | .tasks[] | select(.name == \"coverage\") | .runAfter[$idx])" "$target_file"
    done
}
remove_item_from_array clone "$pipeline"
remove_item_from_array init "$pipeline"
yq -i '(.spec | .tasks[] | select(.name == "coverage") | .runAfter) += ["git-clone", "initialize"]' "$pipeline"
yq -i '(.spec | .tasks[] | select(.name == "coverage") | .runAfter) |= unique' "$pipeline"
