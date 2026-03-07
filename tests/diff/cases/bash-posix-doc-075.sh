#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 75: wait should drop reaped status entries after reporting.
sleep 0.02 & p075=$!
set +e
wait "$p075"; rc1=$?
err2="$(wait "$p075" 2>&1)"; rc2=$?
set -e
printf 'JM:075:first=%s second=%s seconderr=%s\n' "$rc1" "$rc2" "$err2"
