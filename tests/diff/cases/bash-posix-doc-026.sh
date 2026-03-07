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
printf 'JM:026:first=%s jobs=%s second=%s err=%s\n' "$rc1" "$jobs_out" "$rc2" "$wait2_err"
