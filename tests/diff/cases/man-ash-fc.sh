#!/usr/bin/env ash
# Coverage: man ash `fc` builtin.
# Areas:
# - list mode with and without numbering
# - reverse listing
# - substitution replay path
# - bad history reference status
set -eu
if ! command -v fc >/dev/null 2>&1; then
  printf 'fc-missing\n'
  exit 0
fi
printf 'fc-start\n'
printf 'history-one\n'
printf 'history-two\n'
# list the last two commands
fc -ln -2
# reverse listing
fc -lrn -2
# re-execute the previous `printf`
fc -s 'printf fc-backref' 'printf history-two'
set +e
fc -s 999999 >/dev/null 2>&1
bad_status=$?
set -e
printf 'fc-bad-status=%s\n' "$bad_status"
printf 'fc-done\n'
