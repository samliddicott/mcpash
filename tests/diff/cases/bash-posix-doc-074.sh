#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 74: CHLD traps and wait behavior.
c074=0
trap 'c074=$((c074 + 1))' CHLD
sleep 0.05 & p1=$!
sleep 0.10 & p2=$!
set +e
wait "$p1"; rc1=$?
wait "$p2"; rc2=$?
set -e
# Give trap execution a moment to flush.
sleep 0.05
ok=0
if [ "$rc1" -eq 145 ] && [ "$rc2" -eq 145 ] && [ "$c074" -ge 1 ]; then
  ok=1
fi
echo "JM:074:ok=$ok rc1=$rc1 rc2=$rc2"
