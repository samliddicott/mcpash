#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - array/hash value expansion with pattern trim/replace
# - element-specific trim/replace
# - key listing and length
declare -a arr
arr=(ab xxabyy abz)
echo "arr-len:${#arr[@]}"
echo "arr-el:${arr[0]/ab/Q}:${arr[1]#xx}:${arr[2]%z}"
printf 'arr-at-repl:'; printf '<%s>' "${arr[@]/ab/Q}"; echo
printf 'arr-star-repl:'; printf '<%s>' "${arr[*]/ab/Q}"; echo
printf 'arr-at-trim:'; printf '<%s>' "${arr[@]#a}"; echo

declare -A map
map[a]="abv"
map[b]="xxabyy"
map[c]="abz"
echo "map-len:${#map[@]}"
echo "map-el:${map[a]/ab/Q}:${map[b]#xx}:${map[c]%z}"
printf 'map-at-repl:'; printf '<%s>' "${map[@]/ab/Q}"; echo
printf 'map-star-repl:'; printf '<%s>' "${map[*]/ab/Q}"; echo
printf '%s\n' "${!map[@]}" | sort | tr '\n' ' ' | sed 's/[[:space:]]*$//'
