#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: mapfile/readarray core flags and array population.
set +e
export BASH_COMPAT=50
tmp="${TMPDIR:-/tmp}/mctash-mapfile-$$.txt"
trap 'rm -f "$tmp"' EXIT

printf 'a\nb\nc\n' >"$tmp"
mapfile -t arr <"$tmp"
s_map=$?
printf 'm:%s:%s\n' "$s_map" "${#arr[@]}"

printf 'x\ny\n' >"$tmp"
mapfile -t arr2 <"$tmp"
printf 't:%s\n' "${#arr2[@]}"

printf 'q\nr\ns\n' >"$tmp"
readarray -t -n 2 arr3 <"$tmp"
printf 'n:%s\n' "${#arr3[@]}"

printf 'u\nv\nw\n' >"$tmp"
mapfile -s 1 -t arr4 <"$tmp"
printf 'o:%s\n' "${#arr4[@]}"
