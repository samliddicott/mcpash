#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 28: promptvars/PS1 behavior in POSIX mode.
if command -v script >/dev/null 2>&1; then
  out="$(script -qec "bash --posix -i -c 'v=VV; shopt -u promptvars; PS1=\"\${v} ! !! > \"; :; exit'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" | sed -n '1,4p'
else
  echo JM:028:noscript
fi
