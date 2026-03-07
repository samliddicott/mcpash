#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 26: wait retains status semantics after job notifications.
sleep 0.03 & p=$!
set +e
wait "$p"; rc1=$?
jobs_out="$(jobs 2>&1)"
wait2_err="$(wait "$p" 2>&1)"; rc2=$?
set -e
err_has=0
if printf '%s\n' "$wait2_err" | grep -q 'not a child of this shell'; then
  err_has=1
fi
jobs_has=0
if [ -n "$jobs_out" ]; then
  jobs_has=1
fi
printf 'JM:026:first=%s jobs_has=%s second=%s err_has=%s\n' "$rc1" "$jobs_has" "$rc2" "$err_has"
