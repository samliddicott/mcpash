#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 27: vi `v` command editor preference behavior.
if command -v script >/dev/null 2>&1; then
  tmp_out="$(mktemp)"
  trap '/bin/rm -f "$tmp_out"' EXIT
  set +e
  script -qec "VISUAL=false EDITOR=false bash --posix -i -c 'set -o vi; fc -s 2>/dev/null || true'" /dev/null >"$tmp_out" 2>/dev/null
  rc=$?
  set -e
  out="$(tr -d '\r' < "$tmp_out")"
  has_text=0
  [ -n "$out" ] && has_text=1
  echo "JM:027:rc=$rc has_text=$has_text"
else
  echo JM:027:noscript
fi
