#!/usr/bin/env ash
# Coverage: man ash trap builtin.
# Areas:
# - setting handlers for EXIT/INT
# - ignoring HUP
# - listing and clearing handlers
# - invalid signal specification status
set -eu
trap 'echo trap-exit' EXIT
trap '' HUP
trap 'echo trap-int' INT

printf 'pre-trap\n'

trap_line="$(trap)"
case "$trap_line" in
  *INT*trap-int*) printf 'trap-list=int\n' ;;
  *) printf 'trap-list=missing\n' ;;
esac

trap - INT
after_clear="$(trap)"
case "$after_clear" in
  *INT*) printf 'trap-clear=bad\n' ;;
  *) printf 'trap-clear=ok\n' ;;
esac

set +e
trap 'printf bad\n' NOTASIG 2>/dev/null
bad_status=$?
set -e
printf 'trap-bad-status=%s\n' "$bad_status"

kill -HUP $$
printf 'post-hup\n'
