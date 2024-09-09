#!/usr/bin/env bash
set -euo pipefail
pipeline=$1
expression='(.spec.tasks[] | select(.name == "coverage") | .runAfter) += ["init", "clone"]'
yq -i "$expression" "$pipeline"