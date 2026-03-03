#!/usr/bin/env ash
# Coverage: ulimit flag matrix for this ash target.
# Areas:
# - soft/hard query forms
# - resource selectors: -f, -n, -c, -v, -d, -s, -t, -l, -m, -p
# - invalid option status
set -eu
. "$(dirname "$0")/_ulimit_safety.inc"
apply_ulimit_safety_caps

f_soft="$(ulimit -S -f)"
n_soft="$(ulimit -S -n)"
n_hard="$(ulimit -H -n)"
c_soft="$(ulimit -S -c)"
v_soft="$(ulimit -S -v)"
d_soft="$(ulimit -S -d)"
s_soft="$(ulimit -S -s)"
t_soft="$(ulimit -S -t)"
l_soft="$(ulimit -S -l)"
m_soft="$(ulimit -S -m)"
p_soft="$(ulimit -S -p)"

set +e
ulimit -Z >/dev/null 2>&1
st_bad=$?
set -e

printf 'f-soft=%s\n' "$f_soft"
printf 'n-soft=%s\n' "$n_soft"
printf 'n-hard=%s\n' "$n_hard"
printf 'c-soft=%s\n' "$c_soft"
printf 'v-soft=%s\n' "$v_soft"
printf 'd-soft=%s\n' "$d_soft"
printf 's-soft=%s\n' "$s_soft"
printf 't-soft=%s\n' "$t_soft"
printf 'l-soft=%s\n' "$l_soft"
printf 'm-soft=%s\n' "$m_soft"
printf 'p-soft=%s\n' "$p_soft"
printf 'bad=%s\n' "$st_bad"
