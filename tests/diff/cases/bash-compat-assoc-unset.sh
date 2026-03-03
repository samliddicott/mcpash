#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - unset assoc key with quoted subscript
# - key/value presence checks after deletion
declare -A map
map[a]=one
map[b]=two
unset 'map[a]'
echo "n:${#map[@]} a:${map[a]-unset} b:${map[b]-unset}"
printf '%s\n' "${!map[@]}" | sort | tr '\n' ' ' | sed 's/[[:space:]]*$//'
