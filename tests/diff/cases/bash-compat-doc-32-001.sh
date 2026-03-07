#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.32.001: [[ < > ]] collation behavior probe (same axis).
set +e
LC_ALL=C [[ b < c ]]; rc1=$?
LC_ALL=C [[ c > b ]]; rc2=$?
set -e
printf 'JM:BCOMPAT_32_001:C:%s:%s\n' "$rc1" "$rc2"
