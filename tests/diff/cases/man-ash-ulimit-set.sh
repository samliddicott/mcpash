#!/usr/bin/env ash
# Coverage: ulimit set paths using current values.
# Areas:
# - -S/-H set with existing values
# - per-resource set parity for -n and -f
set -eu

n_soft="$(ulimit -S -n)"
n_hard="$(ulimit -H -n)"
f_soft="$(ulimit -S -f)"
f_hard="$(ulimit -H -f)"

set +e
ulimit -S -n "$n_soft"
st_sn=$?
ulimit -H -n "$n_hard"
st_hn=$?
ulimit -S -f "$f_soft"
st_sf=$?
ulimit -H -f "$f_hard"
st_hf=$?
set -e

printf 'set-sn=%s\n' "$st_sn"
printf 'set-hn=%s\n' "$st_hn"
printf 'set-sf=%s\n' "$st_sf"
printf 'set-hf=%s\n' "$st_hf"
