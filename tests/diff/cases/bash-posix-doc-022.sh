#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 22: job status message format for non-zero exit.
if command -v script >/dev/null 2>&1; then
  tmp_out="$(mktemp)"
  trap '/bin/rm -f "$tmp_out"' EXIT
  set +e
  script -qec "bash --posix -i -c 'set -m; sh -c \"exit 7\" & wait %1 2>/dev/null; jobs -l'" /dev/null >"$tmp_out" 2>/dev/null
  rc=$?
  set -e
  out="$(tr -d '\r' < "$tmp_out")"
  done_fmt=0
  printf '%s\n' "$out" | grep -Eq 'Done\(|Exit|done' && done_fmt=1
  echo "JM:022:rc=$rc done_fmt=$done_fmt"
else
  echo JM:022:noscript
fi
