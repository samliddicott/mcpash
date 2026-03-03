#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - dedicated collection slicing semantics for [@] and [*]
# - quoted context behavior with offsets/lengths
declare -a arr
arr=(aa bb cc dd)
printf 'arr-at:'; printf '<%s>' "${arr[@]:1:2}"; echo
printf 'arr-star:'; printf '<%s>' "${arr[*]:1:2}"; echo
printf 'arr-at-neg:'; printf '<%s>' "${arr[@]: -2:1}"; echo
printf 'arr-star-neg:'; printf '<%s>' "${arr[*]: -2:1}"; echo
