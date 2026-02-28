#!/usr/bin/env ash
# Coverage: ulimit error/status matrix.
# Areas:
# - invalid option and invalid numeric value
# - too-large numeric overflow handling
# - extra-operand rejection
set -eu

set +e
ulimit -Z >/dev/null 2>&1
st_bad_opt=$?
ulimit -S -n notnum >/dev/null 2>&1
st_bad_num=$?
ulimit -S -n 999999999999999999999 >/dev/null 2>&1
st_huge=$?
ulimit -S -n 123 456 >/dev/null 2>&1
st_extra=$?
set -e

printf 'bad-opt=%s\n' "$st_bad_opt"
printf 'bad-num=%s\n' "$st_bad_num"
printf 'huge=%s\n' "$st_huge"
printf 'extra=%s\n' "$st_extra"
