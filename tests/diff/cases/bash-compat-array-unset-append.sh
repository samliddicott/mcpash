#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - unset indexed element keeps sparse array
# - arr+=(...) appends at next index
# - ${arr[@]} and ${!arr[@]} after append
declare -a arr
arr=(a b c)
unset 'arr[1]'
arr+=(d e)
echo "len:${#arr[@]}"
echo "vals:${arr[@]}"
idx="$(printf '%s ' "${!arr[@]}")"
echo "idx:${idx% }"
