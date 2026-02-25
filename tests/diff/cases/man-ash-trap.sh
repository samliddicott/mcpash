#!/usr/bin/env ash
# Coverage: man ash trap builtin (setting handlers, ignoring, EXIT, INT).
set -euo pipefail
trap 'printf trap-exit\n' EXIT
trap '' HUP
trap 'printf trap-int\n' INT

printf 'pre-trap\n'
kill -HUP $$
printf 'post-hup\n'
kill -INT $$
printf 'post-int\n'
