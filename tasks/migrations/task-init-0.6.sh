#!/usr/bin/env bash
set -euo pipefail
pipeline=$1
coverage_task_exists=$(
yq '
.spec.tasks[] | select(.name == "coverage") |
.taskRef.params[] | select(.name == "bundle") |
.value | contains("quay.io/mytestworkload/test-renovate-updates-task-coverage")
' "$pipeline"
)

if [ -z "$coverage_task_exists" ]
then
  task_def='{
  "name": "coverage",
  "taskRef": {
    "params": [
      {"name": "name", "value": "coverage"},
      {"name": "bundle", "value": "quay.io/mytestworkload/test-renovate-updates-task-coverage@sha256:f1035491051492d27ba637bfe626fee532a1e9c2b547cae79fc7504a62fbf763"},
      {"name": "kind", "value": "task"}
    ]
  },
  "runAfter": ["test"]
}'
  yq -i ".spec.tasks += ${task_def}" "$pipeline"
fi
