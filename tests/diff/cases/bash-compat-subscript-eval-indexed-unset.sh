#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - dedicated indexed unset arithmetic semantics
# - unset side effects from arithmetic expressions
declare -a arr
arr=(a b c d e)
i=0
unset 'arr[i++]'
unset 'arr[i+=2]'
unset 'arr[-1]'
idx="$(printf '%s ' "${!arr[@]}")"
echo "i:$i idx:${idx% } vals:${arr[@]}"
