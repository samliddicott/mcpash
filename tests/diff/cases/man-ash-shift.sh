#!/usr/bin/env ash
# Coverage: man ash 'shift' builtin (default shift, shifting by >1, error handling).
set -euo pipefail
set -- a b c d
echo "shift-1=$1"
shift
printf 'shifted=%s:%s\n' "$1" "$2"
shift 2
printf 'shifted-2=%s\n' "$1"
set --  x y z
set +e
shift 10
status=$?
set -e
if [ "$status" -ne 0 ]; then
  printf 'shift-error=%s\n' "$status"
fi
