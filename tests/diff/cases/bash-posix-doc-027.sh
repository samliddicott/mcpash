#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 27: vi-mode `v` path probe in interactive lane.
# This row remains an interactive probe; we compare normalized effect markers.
if command -v script >/dev/null 2>&1; then
  ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
  if [[ -n "${MCTASH_MODE-}" ]]; then
    shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix -i"
  else
    shell_cmd='bash --posix -i'
  fi
  tmp_out="$(mktemp)"
  trap '/bin/rm -f "$tmp_out"' EXIT
  set +e
  script -qec "VISUAL=false EDITOR=false ${shell_cmd} -c 'set -o vi; fc -s 2>/dev/null || true'" /dev/null >"$tmp_out" 2>/dev/null
  set -e
  out="$(tr -d '\r' < "$tmp_out")"
  has_text=0
  [ -n "$out" ] && has_text=1
  echo "JM:027:has_text=$has_text"
else
  echo JM:027:noscript
fi
