#!/usr/bin/bash

echo "============================="
echo $@

echo
echo "============================="
echo "{{ upgrades }}"

echo
echo "============================="
echo "{{{ toJSON upgrades }}}"

echo
echo "============================="
git status

echo
echo "============================="
git diff

