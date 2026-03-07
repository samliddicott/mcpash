#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.50.002: hash -l output when table empty.
hash -r
set +e
out="$(hash -l 2>&1)"; rc=$?
set -e
printf 'JM:BCOMPAT_50_002:rc=%s out=%s\n' "$rc" "$out"
