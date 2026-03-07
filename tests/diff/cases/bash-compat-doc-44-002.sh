#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.44.002: subshell loop-state behavior for break.
set +e
for i in 1 2; do
  ( break )
  echo "JM:BCOMPAT_44_002:loop:$i"
done
rc=$?
set -e
echo "JM:BCOMPAT_44_002:rc=$rc"
