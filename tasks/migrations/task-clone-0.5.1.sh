#!/usr/bin/env bash
set -euo pipefail
pipeline=$1

# update tasks: clone, test, coverage

for task in clone "test" coverage; do
  expr="
  .spec.tasks[] | select(.name == \"${task}\") |
  .workspaces[] | select(.name == \"source\" and .workspace == \"workspace\")
  "
  ws=$(yq "$expr" "$pipeline")

  if [ -z "$ws" ]
  then
    new_ws='[{"name": "source", "workspace": "workspace"}]'
    expr="(.spec.tasks[] | select(.name == \"${task}\") | .workspaces) += ${new_ws}"
    yq -i "$expr" "$pipeline"
  fi
done

if ! yq '.spec.workspaces' "$pipeline" | grep -q "\- workspace" >/dev/null
then
  yq -i '.spec.workspaces += [{"name": "workspace"}]' "$pipeline"
fi