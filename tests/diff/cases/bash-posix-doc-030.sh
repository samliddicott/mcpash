#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 30: `!` in double quotes should not trigger history expansion.
if command -v script >/dev/null 2>&1; then
  out="$(script -qec "bash --posix -i -c 'set -H; echo \"a!b\"'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" | sed -n '1,4p'
else
  echo JM:030:noscript
fi
