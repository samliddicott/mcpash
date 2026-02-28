#!/usr/bin/env ash
# Coverage: trap signal matrix extensions.
# Areas:
# - numeric signal specification
# - clear handler and verify listing
# - invalid signal status
set -eu

trap 'echo trap-term' TERM
trap 'echo trap-usr1' 10
list1="$(trap)"
case "$list1" in
  *TERM*trap-term*) echo term-set ;;
  *) echo term-missing ;;
esac
case "$list1" in
  *USR1*trap-usr1*|*10*trap-usr1*) echo usr1-set ;;
  *) echo usr1-missing ;;
esac

trap - 10
list2="$(trap)"
case "$list2" in
  *USR1*|*10*) echo usr1-clear-bad ;;
  *) echo usr1-clear-ok ;;
esac

set +e
trap 'echo bad' NOT_A_SIGNAL >/dev/null 2>&1
st_bad=$?
set -e
printf 'trap-bad=%s\n' "$st_bad"
