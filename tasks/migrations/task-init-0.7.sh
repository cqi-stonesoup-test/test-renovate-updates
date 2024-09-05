#!/usr/bin/env bash
set -euo pipefail
pipeline=$1

if ! yq '.spec.tasks[] | select(.name == "test") | .runAfter' "$pipeline" | grep -q "\- clone" >/dev/null
then
  yq -i '(.spec.tasks[] | select(.name == "test")) += {"runAfter": ["clone"]}' "$pipeline"
fi
