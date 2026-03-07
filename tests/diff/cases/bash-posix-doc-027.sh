#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 27: vi `v` command editor preference behavior.
if command -v script >/dev/null 2>&1; then
  out="$(script -qec "VISUAL=false EDITOR=false bash --posix -i -c 'set -o vi; fc -s 2>/dev/null || true'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" | sed -n '1,6p'
else
  echo JM:027:noscript
fi
