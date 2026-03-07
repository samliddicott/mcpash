#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 22: job status message format for non-zero exit.
if command -v script >/dev/null 2>&1; then
  out="$(script -qec "bash --posix -i -c 'set -m; sh -c \"exit 7\" & wait %1 2>/dev/null; jobs -l'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" | grep -E 'Done\(|Exit|done' | sed -n '1,3p'
else
  echo JM:022:noscript
fi
