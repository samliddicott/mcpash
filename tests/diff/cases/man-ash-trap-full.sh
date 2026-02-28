#!/usr/bin/env ash
# Coverage: trap extended matrix.
# Areas:
# - set/clear multiple signals in one command
# - install/clear EXIT via numeric 0
# - trap action execution on TERM/INT
# - invalid signal specifications
set -eu

set +e
trap : HUP INT QUIT TERM USR1 USR2
st_set_many=$?
trap - HUP INT QUIT TERM USR1 USR2
st_clear_many=$?
trap 'echo exit-hook' 0
st_set0=$?
trap - 0
st_clear0=$?
trap : 999 >/dev/null 2>&1
st_bad_999=$?
trap : NOT_A_SIGNAL >/dev/null 2>&1
st_bad_name=$?
set -e
printf 'set-many=%s\n' "$st_set_many"
printf 'clear-many=%s\n' "$st_clear_many"
printf 'set-0=%s\n' "$st_set0"
printf 'clear-0=%s\n' "$st_clear0"
printf 'bad-999=%s\n' "$st_bad_999"
printf 'bad-name=%s\n' "$st_bad_name"

trap 'echo term-trap' TERM
kill -TERM $$
printf 'after-term\n'

trap 'echo int-trap' INT
kill -INT $$
printf 'after-int\n'
