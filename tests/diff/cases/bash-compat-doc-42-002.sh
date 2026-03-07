#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.42.002: single quotes in double-quoted ${...} word expansion.
v='abc}'
set +e
out="$(eval 'printf "%s\n" "${v%\'}\'}"' 2>&1)"; rc=$?
set -e
printf 'JM:BCOMPAT_42_002:rc=%s out=%s\n' "$rc" "$out"
