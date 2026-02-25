#!/usr/bin/env ash
# Coverage: man ash `fc` builtin (listing history, reverse order, and `-s` re-execution).
set -euo pipefail
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
fc -ln -2 | tail -n1
# re-execute the previous `printf`
fc -s 'printf fc-backref' 'printf history-two'
printf 'fc-done\n'
