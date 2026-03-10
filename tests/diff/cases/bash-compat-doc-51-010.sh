#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.010: parse command substitution with extglob syntax before enabling extglob.
set +e
f() { echo "$(echo @(a|b))"; }
rc_def=$?
shopt -s extglob
out="$(f 2>&1)"; rc_run=$?
set -e
case "$out" in
  *"syntax error"*) parse_ok=0 ;;
  *) parse_ok=1 ;;
esac
echo "JM:BCOMPAT_51_010:def=$rc_def run=$rc_run parse_ok=$parse_ok"
