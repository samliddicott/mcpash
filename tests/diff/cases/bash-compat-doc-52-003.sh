#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.52.003: interactive shell job notification while sourcing.
if command -v script >/dev/null 2>&1; then
  tmp="$(mktemp)"
  trap 'rm -f "$tmp"' EXIT
  cat >"$tmp" <<'SH'
set -m
sleep 0.1 &
echo sourced
sleep 0.2
SH
  out="$(script -qec "bash -i '$tmp'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" | sed -n '1,12p'
else
  echo JM:BCOMPAT_52_003:noscript
fi
