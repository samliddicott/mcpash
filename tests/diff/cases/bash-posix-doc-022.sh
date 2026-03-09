#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 22: non-zero completed jobs use Done(status)-style state.
ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${MCTASH_MODE-}" ]]; then
  runner_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  runner_cmd='bash --posix'
fi

tmp_out="$(mktemp)"
trap '/bin/rm -f "$tmp_out"' EXIT
set +e
eval "${runner_cmd} -c 'set -m; sh -c \"exit 7\" & sleep 0.2; jobs -l'" >"$tmp_out" 2>/dev/null
rc=$?
set -e
out="$(cat "$tmp_out")"
done_status=0
printf '%s\n' "$out" | grep -q 'Done(7)' && done_status=1
echo "JM:022:rc=$rc done_status=$done_status"
