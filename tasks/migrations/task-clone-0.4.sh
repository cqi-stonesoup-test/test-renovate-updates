#!/usr/bin/env bash
pipeline=$1
task_name=clone
yq -i "(.spec.tasks[] | select(.name == \"${task_name}\") | .params) += {\"name\": \"sslVerify\", \"value\": \"false\"}" "$pipeline"
