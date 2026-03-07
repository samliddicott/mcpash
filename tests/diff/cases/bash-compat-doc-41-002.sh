#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.41.002: single-quote treatment in ${...} word part.
v='abc}'
set +e
out="$(eval 'printf "%s\n" "${v%\'}\'}"' 2>&1)"; rc=$?
set -e
printf 'JM:BCOMPAT_41_002:rc=%s out=%s\n' "$rc" "$out"
