#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 75: wait should drop reaped status entries after reporting.
sleep 0.02 & p075=$!
set +e
wait "$p075"; rc1=$?
err2="$(wait "$p075" 2>&1)"; rc2=$?
set -e
err_has=0
if printf '%s\n' "$err2" | grep -q 'not a child of this shell'; then
  err_has=1
fi
printf 'JM:075:first=%s second=%s err_has=%s\n' "$rc1" "$rc2" "$err_has"
