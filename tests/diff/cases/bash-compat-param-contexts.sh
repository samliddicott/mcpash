#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - quoted vs unquoted parameter expansion contexts
# - assignment RHS context
# - array/hash expansions in argument context
declare -a arr
arr=("a b" "cd")
declare -A map
map[x]="p q"
map[y]="rs"

u=${arr[@]}
q="${arr[@]}"
s="${arr[*]}"
echo "scalar-u:$u"
echo "scalar-q:$q"
echo "scalar-s:$s"

printf 'argv-u:'; for x in ${arr[@]}; do printf '<%s>' "$x"; done; echo
printf 'argv-q:'; for x in "${arr[@]}"; do printf '<%s>' "$x"; done; echo
printf 'argv-s:'; for x in "${arr[*]}"; do printf '<%s>' "$x"; done; echo

assign_u=${map[@]/ /_}
assign_q="${map[@]/ /_}"
echo "assign-u:$assign_u"
echo "assign-q:$assign_q"
printf 'map-q:'; for x in "${map[@]/ /_}"; do printf '<%s>' "$x"; done; echo
