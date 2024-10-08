#!/usr/bin/env bash
pipeline=$1
task_name=clone
param=$(yq ".spec.tasks[] | select(.name == \"${task_name}\") | .params[] | select(.name == \"sslVerify\" and .value == \"false\")" "$pipeline")
if [ -z "$param" ]
then
  yq -i "(.spec.tasks[] | select(.name == \"${task_name}\") | .params) += {\"name\": \"sslVerify\", \"value\": \"false\"}" "$pipeline"
fi
