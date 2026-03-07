#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.31.002: quoted RHS of [[ =~ ]] behavior.
s='ab'
set +e
[[ $s =~ a. ]]; rc_unq=$?
[[ $s =~ "a." ]]; rc_q=$?
set -e
printf 'JM:BCOMPAT_31_002:unq=%s q=%s\n' "$rc_unq" "$rc_q"
