#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.41.001: `time` reserved word option parsing in POSIX mode.
set +e
out="$(time -p : 2>&1)"; rc=$?
set -e
printf 'JM:BCOMPAT_41_001:rc=%s tail=%s\n' "$rc" "$(printf '%s\n' "$out" | tail -n1)"
