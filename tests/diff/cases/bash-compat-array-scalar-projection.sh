#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - scalar projection of indexed array variable (${arr})
# - explicit index fetch (${arr[0]}, ${arr[1]})
declare -a arr
arr=(first second third)
echo "scalar:${arr}"
echo "i0:${arr[0]} i1:${arr[1]}"
