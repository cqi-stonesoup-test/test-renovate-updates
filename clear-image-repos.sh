#!/usr/bin/env bash

set -euo pipefail

find ./definitions/ -maxdepth 1 -name "task-*.yaml" | \
while read -r task_file
do
    filename="$(basename "$task_file")"
    image_repo=mytestworkload/test-renovate-updates-${filename%-*}
    for tag in $(curl -sL "https://quay.io/api/v1/repository/${image_repo}/tag/?onlyActiveTags=true" | jq -r '.tags[].name' | grep "^[0-9]\.[0-9]-[0-9a-f]\+$")
    do
        echo -n "deleting docker://quay.io/${image_repo}:${tag} ..."
        skopeo delete "docker://quay.io/${image_repo}:${tag}"
        echo " DELETED!"
    done
done

image_repo=mytestworkload/test-renovate-updates-pipeline
for tag in $(curl -sL "https://quay.io/api/v1/repository/${image_repo}/tag/?onlyActiveTags=true" | jq -r '.tags[].name')
do
    echo -n "deleting docker://quay.io/${image_repo}:${tag} ..."
    skopeo delete "docker://quay.io/${image_repo}:${tag}"
    echo " DELETED!"
done
