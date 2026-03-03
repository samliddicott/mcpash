#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Bash-compat gated indexed/assoc declaration + assignment parity slice.
declare -a arr
arr[0]=a
arr[1]=b
echo "a1:${arr[1]} s:${arr}"

declare -A map
map[k]=v
echo "mk:${map[k]}"
