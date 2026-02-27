#!/usr/bin/env ash
# Coverage: man ash 'shift' builtin (default shift, shifting by >1, error handling).
set -eu
set -- a b c d
echo "shift-1=$1"
shift
printf 'shifted=%s:%s\n' "$1" "$2"
shift 2
printf 'shifted-2=%s\n' "$1"
set --  x y z
shift 10 >/dev/null 2>&1 || true
