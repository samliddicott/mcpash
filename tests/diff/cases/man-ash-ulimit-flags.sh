#!/usr/bin/env ash
# Coverage: ulimit flag matrix for this ash target.
# Areas:
# - soft/hard query forms
# - resource selectors: -f, -n, -c, -v
# - invalid option status
set -eu

f_soft="$(ulimit -S -f)"
n_soft="$(ulimit -S -n)"
n_hard="$(ulimit -H -n)"
c_soft="$(ulimit -S -c)"
v_soft="$(ulimit -S -v)"

set +e
ulimit -Z >/dev/null 2>&1
st_bad=$?
set -e

printf 'f-soft=%s\n' "$f_soft"
printf 'n-soft=%s\n' "$n_soft"
printf 'n-hard=%s\n' "$n_hard"
printf 'c-soft=%s\n' "$c_soft"
printf 'v-soft=%s\n' "$v_soft"
printf 'bad=%s\n' "$st_bad"
