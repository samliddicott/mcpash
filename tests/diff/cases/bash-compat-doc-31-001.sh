#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.31.001: [[ < > ]] collation behavior probe.
set +e
LC_ALL=C [[ Z < a ]]; rc1=$?
LC_ALL=C [[ a > Z ]]; rc2=$?
set -e
printf 'JM:BCOMPAT_31_001:C:%s:%s\n' "$rc1" "$rc2"
