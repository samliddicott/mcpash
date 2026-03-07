#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 48: bg output format (no current/previous indicator)
if command -v script >/dev/null 2>&1; then
  out48="$(script -qec "bash --posix -i -c 'set -m; sleep 0.2 & fg %1 >/dev/null 2>&1; sleep 0.2 & bg %1'" /dev/null 2>/dev/null | tr -d '\r' | sed -n '1,5p')"
  # Normalize and report whether + or - markers appear.
  if printf '%s
' "$out48" | grep -Eq '^\[[0-9]+\][[:space:]]+\+|-'; then
    echo JM:048:marker
  else
    echo JM:048:nomarker
  fi
else
  echo JM:048:noscript
fi

