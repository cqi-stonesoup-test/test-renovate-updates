#!/usr/bin/env bash
pipeline=$1
yq -i 'del(
.spec.tasks[] | select(.name == "clone") |
.params[] | select(.name == "sslVerify" and .value == "false")
)' "$pipeline"