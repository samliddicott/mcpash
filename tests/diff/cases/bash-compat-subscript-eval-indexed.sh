#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - indexed subscripts use arithmetic evaluation
# - assignment/read/unset all honor arithmetic index expressions
declare -a arr
arr[0]=z
arr[1]=one
i=1
arr[i+1]=two
echo "v2:${arr[2]} via:${arr[i+1]}"
unset 'arr[i+1]'
echo "after:${arr[2]-unset}"
