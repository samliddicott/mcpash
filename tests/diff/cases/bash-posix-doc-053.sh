#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 53: fc listing modified marker omitted
set +e
fc -l >/tmp/fc53.out 2>/tmp/fc53.err
st=$?
set -e
if [[ $st -ne 0 ]]; then
  echo JM:053:st:${st}
else
  if grep -q '\*' /tmp/fc53.out; then echo JM:053:star; else echo JM:053:nostar; fi
fi
rm -f /tmp/fc53.out /tmp/fc53.err

