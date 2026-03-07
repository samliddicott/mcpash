#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.40.001: locale-vs-ASCII [[ ordering probe.
set +e
LC_ALL=C [[ Z < a ]]; rc_c=$?
LC_ALL=C.UTF-8 [[ Z < a ]]; rc_utf=$?
set -e
printf 'JM:BCOMPAT_40_001:C=%s UTF=%s\n' "$rc_c" "$rc_utf"
