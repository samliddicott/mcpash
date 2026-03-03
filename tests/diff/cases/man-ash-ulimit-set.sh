#!/usr/bin/env ash
# Coverage: ulimit set paths using current values.
# Areas:
# - -S/-H set with existing values
# - per-resource set parity for -n, -f, -c, -v
set -eu

n_soft="$(ulimit -S -n)"
n_hard="$(ulimit -H -n)"
f_soft="$(ulimit -S -f)"
f_hard="$(ulimit -H -f)"
c_soft="$(ulimit -S -c)"
c_hard="$(ulimit -H -c)"
v_soft="$(ulimit -S -v)"
v_hard="$(ulimit -H -v)"

set +e
ulimit -S -n "$n_soft"
st_sn=$?
ulimit -H -n "$n_hard"
st_hn=$?
ulimit -S -f "$f_soft"
st_sf=$?
ulimit -H -f "$f_hard"
st_hf=$?
ulimit -S -c "$c_soft"
st_sc=$?
ulimit -H -c "$c_hard"
st_hc=$?
ulimit -S -v "$v_soft"
st_sv=$?
ulimit -H -v "$v_hard"
st_hv=$?
set -e

printf 'set-sn=%s\n' "$st_sn"
printf 'set-hn=%s\n' "$st_hn"
printf 'set-sf=%s\n' "$st_sf"
printf 'set-hf=%s\n' "$st_hf"
printf 'set-sc=%s\n' "$st_sc"
printf 'set-hc=%s\n' "$st_hc"
printf 'set-sv=%s\n' "$st_sv"
printf 'set-hv=%s\n' "$st_hv"
