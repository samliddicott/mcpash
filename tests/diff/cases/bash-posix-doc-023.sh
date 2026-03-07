#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 23: stopped job status message format.
if command -v script >/dev/null 2>&1; then
  out="$(script -qec "bash --posix -i -c 'set -m; sleep 5 & kill -TSTP %1; jobs -l; kill -TERM %1 2>/dev/null'" /dev/null 2>/dev/null | tr -d '\r')"
  printf '%s\n' "$out" \
    | grep -E 'Stopped|SIGTSTP|SIGSTOP' \
    | sed -n '1,3p' \
    | sed -E 's/[0-9]{4,}/PID/g'
else
  echo JM:023:noscript
fi
