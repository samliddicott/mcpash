#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Bash-compat gated indexed/assoc declaration + assignment parity slice.
declare -a arr
arr[0]=a
arr[1]=b
arr[2]=c
echo "a1:${arr[1]} s:${arr} n:${#arr[@]} at:${arr[@]} star:${arr[*]}"
unset arr[1]
echo "n2:${#arr[@]} at2:${arr[@]} i1:${arr[1]}"

declare -A map
map[k]=v
map[q]=w
echo "mk:${map[k]} mq:${map[q]}"
