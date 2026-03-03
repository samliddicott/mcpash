#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - dedicated indexed assignment arithmetic semantics
# - assignment side effects from arithmetic expressions
declare -a arr
arr[0]=z
i=0
arr[i++]=a
arr[++i]=b
arr[1+1]=c
idx="$(printf '%s ' "${!arr[@]}")"
echo "i:$i idx:${idx% } v0:${arr[0]-u} v1:${arr[1]-u} v2:${arr[2]-u}"
