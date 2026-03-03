#!/usr/bin/env ash
# Coverage: ulimit soft/hard option interaction matrix.
# Areas:
# - split and combined -S/-H query forms
# - set path with combined flags using current hard value
set -eu
. "$(dirname "$0")/_ulimit_safety.inc"
apply_ulimit_safety_caps

set +e
ulimit -S -H -n >/dev/null 2>&1
st_split=$?
ulimit -H -S -n >/dev/null 2>&1
st_split_rev=$?
ulimit -HS -n >/dev/null 2>&1
st_comb=$?
ulimit -SH -n >/dev/null 2>&1
st_comb_rev=$?
ulimit -HS -n "$(ulimit -H -n)" >/dev/null 2>&1
st_set_comb=$?
ulimit -SH -n "$(ulimit -H -n)" >/dev/null 2>&1
st_set_comb_rev=$?
set -e

printf 'split=%s\n' "$st_split"
printf 'split-rev=%s\n' "$st_split_rev"
printf 'comb=%s\n' "$st_comb"
printf 'comb-rev=%s\n' "$st_comb_rev"
printf 'set-comb=%s\n' "$st_set_comb"
printf 'set-comb-rev=%s\n' "$st_set_comb_rev"
