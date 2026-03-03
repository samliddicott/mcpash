#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - arithmetic side effects in indexed subscripts (i++, ++i, i+=1)
# - side effects apply across read and unset contexts
declare -a arr
arr=(x y z w)
i=0
echo "r1:${arr[i++]}:i=$i"
echo "r2:${arr[++i]}:i=$i"
i=1
unset 'arr[i+=1]'
idx="$(printf '%s ' "${!arr[@]}")"
echo "unset-side:i=$i:idx:${idx% }"
