#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): '.' and 'source' basics (path, args, status).

set +e
work="./tmp-bash-posix-dot-$$"
mkdir -p "$work"
cat >"$work/lib.sh" <<'LIB'
X=from_lib
printf 'lib-args:%s:%s\n' "$1" "$2"
LIB

set -- P Q
. "$work/lib.sh" A B
printf 'dot:%s:%s:%s\n' "$1" "$2" "$X"

source "$work/lib.sh" C D
printf 'source:%s:%s:%s\n' "$1" "$2" "$X"

( . "$work/missing.sh" >/dev/null 2>&1 )
printf 'dot-miss:%s\n' "$?"

rm -rf "$work"
