#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - indexed array sparse assignment
# - ${!arr[@]} (index listing)
# - ${#arr[@]} length with holes
declare -a arr
arr[0]=zero
arr[2]=two
arr[5]=five
echo "len:${#arr[@]}"
idx="$(printf '%s ' "${!arr[@]}")"
echo "idx:${idx% }"
echo "v2:${arr[2]} v1:${arr[1]-unset}"
