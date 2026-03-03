#!/usr/bin/env ash
# Coverage: non-interactive trap signal install/deliver/clear matrix.
# Areas:
# - install handlers by name
# - deliver signals and verify handler execution
# - clear handlers by name and number
set -eu

for sig in HUP INT TERM USR1 USR2; do
  trap "echo got-$sig" "$sig"
done

kill -HUP $$
kill -INT $$
kill -TERM $$
kill -USR1 $$
kill -USR2 $$

for sig in HUP INT TERM USR1 USR2; do
  trap - "$sig"
done
trap - 1 2 15 10 12
echo trap-matrix-done
