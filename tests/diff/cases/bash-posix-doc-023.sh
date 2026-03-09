#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 23: stopped job status message format.
if command -v script >/dev/null 2>&1; then
  tmp_out="$(mktemp)"
  trap '/bin/rm -f "$tmp_out"' EXIT
  set +e
  script -qec "bash --posix -i -c 'set -m; sleep 5 & p=\$!; kill -TSTP \"\$p\"; jobs -l; kill -TERM \"\$p\" 2>/dev/null'" /dev/null >"$tmp_out" 2>/dev/null
  rc=$?
  set -e
  echo "JM:023:rc=$rc"
else
  echo JM:023:noscript
fi
