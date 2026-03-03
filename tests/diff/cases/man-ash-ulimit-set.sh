#!/usr/bin/env ash
# Coverage: ulimit set paths using current values.
# Areas:
# - -S/-H set with existing values
# - per-resource set parity for -n, -f, -c, -v, -d, -s, -t, -l, -m, -p
# Safety:
# - Never raise or lower limits to new values; only re-apply current live values
#   to avoid stressing the host system during parity runs.
set -eu
. "$(dirname "$0")/_ulimit_safety.inc"
apply_ulimit_safety_caps

n_soft="$(ulimit -S -n)"
n_hard="$(ulimit -H -n)"
f_soft="$(ulimit -S -f)"
f_hard="$(ulimit -H -f)"
c_soft="$(ulimit -S -c)"
c_hard="$(ulimit -H -c)"
v_soft="$(ulimit -S -v)"
v_hard="$(ulimit -H -v)"
d_soft="$(ulimit -S -d)"
d_hard="$(ulimit -H -d)"
s_soft="$(ulimit -S -s)"
s_hard="$(ulimit -H -s)"
t_soft="$(ulimit -S -t)"
t_hard="$(ulimit -H -t)"
l_soft="$(ulimit -S -l)"
l_hard="$(ulimit -H -l)"
m_soft="$(ulimit -S -m)"
m_hard="$(ulimit -H -m)"
p_soft="$(ulimit -S -p)"
p_hard="$(ulimit -H -p)"

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
ulimit -S -d "$d_soft"
st_sd=$?
ulimit -H -d "$d_hard"
st_hd=$?
ulimit -S -s "$s_soft"
st_ss=$?
ulimit -H -s "$s_hard"
st_hs=$?
ulimit -S -t "$t_soft"
st_st=$?
ulimit -H -t "$t_hard"
st_ht=$?
ulimit -S -l "$l_soft"
st_sl=$?
ulimit -H -l "$l_hard"
st_hl=$?
ulimit -S -m "$m_soft"
st_sm=$?
ulimit -H -m "$m_hard"
st_hm=$?
ulimit -S -p "$p_soft"
st_sp=$?
ulimit -H -p "$p_hard"
st_hp=$?
set -e

printf 'set-sn=%s\n' "$st_sn"
printf 'set-hn=%s\n' "$st_hn"
printf 'set-sf=%s\n' "$st_sf"
printf 'set-hf=%s\n' "$st_hf"
printf 'set-sc=%s\n' "$st_sc"
printf 'set-hc=%s\n' "$st_hc"
printf 'set-sv=%s\n' "$st_sv"
printf 'set-hv=%s\n' "$st_hv"
printf 'set-sd=%s\n' "$st_sd"
printf 'set-hd=%s\n' "$st_hd"
printf 'set-ss=%s\n' "$st_ss"
printf 'set-hs=%s\n' "$st_hs"
printf 'set-st=%s\n' "$st_st"
printf 'set-ht=%s\n' "$st_ht"
printf 'set-sl=%s\n' "$st_sl"
printf 'set-hl=%s\n' "$st_hl"
printf 'set-sm=%s\n' "$st_sm"
printf 'set-hm=%s\n' "$st_hm"
printf 'set-sp=%s\n' "$st_sp"
printf 'set-hp=%s\n' "$st_hp"
