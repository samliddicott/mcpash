#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 44: shift_verbose enabled in POSIX mode
set -- a
set +e
shift 2 >/tmp/bp44.err 2>&1
st=$?
set -e
if [[ $st -ne 0 ]] && [[ -s /tmp/bp44.err ]]; then
  echo JM:044:err
else
  echo JM:044:noerr
fi
rm -f /tmp/bp44.err

