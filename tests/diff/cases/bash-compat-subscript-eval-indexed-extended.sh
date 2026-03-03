#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - indexed subscripts with arithmetic expressions and variable references
# - negative index read/assign/unset semantics
# - invalid arithmetic index reports non-zero status in expression context
declare -a arr
arr[0]=zero
arr[2]=two
i=1
j=2

echo "arith:${arr[i+1]}:${arr[(j-1)+1]}:${arr[1*2]}"
echo "neg-read:${arr[-1]-unset}"
arr[-1]=tail
echo "neg-assign:${arr[2]-unset}:${arr[-1]-unset}"
unset 'arr[-1]'
idx="$(printf '%s ' "${!arr[@]}")"
echo "neg-unset:${arr[2]-unset}:len:${#arr[@]}:idx:${idx% }"

(echo "bad:${arr[08]-unset}")
echo "bad-idx-status:$?"
