#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 24: interactive notification timing around list separators.
if command -v script >/dev/null 2>&1; then
  out="$(script -qec "bash --posix -i -c 'set -m; sh -c \"exit 3\" & :; echo after-semicolon; jobs'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" \
    | sed -n '1,8p' \
    | sed -E 's/\[[0-9]+\]/[J]/g; s/[0-9]{4,}/PID/g'
else
  echo JM:024:noscript
fi
