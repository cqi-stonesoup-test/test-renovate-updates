#!/usr/bin/env bash
set -euo pipefail
pipeline=$1
yq -i '(.spec.tasks[] | select(.name == "coverage") | .runAfter) += ["init", "clone"]' "$pipeline"
yq -i '(.spec | .tasks[] | select(.name == "coverage") | .runAfter) |= unique' "$pipeline"