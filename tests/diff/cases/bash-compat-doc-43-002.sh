#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.43.002: function loop-state inheritance for break/continue.
f43() { break; }
set +e
for i in 1 2; do
  f43
  echo "JM:BCOMPAT_43_002:loop:$i"
done
rc=$?
set -e
echo "JM:BCOMPAT_43_002:rc=$rc"
