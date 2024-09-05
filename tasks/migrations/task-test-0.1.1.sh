#!/usr/bin/env bash
set -euo pipefail
pipeline=$1

expr='.spec.tasks[] | select(.name == "test") | .params[] | select(.name == "verbose")'
param=$(yq "${expr}" "$pipeline")

if [ -z "$param" ]
then
  yq -i '(.spec.tasks[] | select(.name == "test") | .params) += [{"name": "verbose", "value": "vv"}]' "$pipeline"
fi
