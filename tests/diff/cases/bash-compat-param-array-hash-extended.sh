#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - element-specific substring/trim/replace for indexed and assoc arrays
# - collection-level substring/replace for [@] and [*] in quoted contexts
declare -a arr
arr=("abXYcd" "pqabrs" "uv")
echo "arr-el-sub:${arr[0]:2:2}:${arr[1]:-2}:${arr[2]:1}"
echo "arr-el-trim:${arr[0]#ab}:${arr[1]%rs}:${arr[2]%%v}"
echo "arr-el-repl:${arr[0]/XY/--}:${arr[1]//ab/QQ}:${arr[2]/v/Z}"
printf 'arr-at-sub:'; printf '<%s>' "${arr[@]:0:2}"; echo
printf 'arr-star-repl:'; printf '<%s>' "${arr[*]/ab/@@}"; echo

declare -A map
map[a]="abXYcd"
map[b]="pqabrs"
map[c]="uv"
echo "map-el-sub:${map[a]:2:2}:${map[b]:-2}:${map[c]:1}"
echo "map-el-trim:${map[a]#ab}:${map[b]%rs}:${map[c]%%v}"
echo "map-el-repl:${map[a]/XY/--}:${map[b]//ab/QQ}:${map[c]/v/Z}"
printf 'map-at-repl:'; printf '<%s>' "${map[@]/ab/@@}"; echo
printf 'map-star-trim:'; printf '<%s>' "${map[*]%rs}"; echo
