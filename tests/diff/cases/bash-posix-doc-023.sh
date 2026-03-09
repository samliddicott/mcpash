#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 23: stopped jobs include a Stopped state in jobs output.
ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${MCTASH_MODE-}" ]]; then
  runner_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  runner_cmd='bash --posix'
fi

tmp_out="$(mktemp)"
trap '/bin/rm -f "$tmp_out"' EXIT
set +e
eval "${runner_cmd} -c 'set -m; sleep 5 & p=\$!; kill -TSTP \"\$p\"; sleep 0.1; jobs -l; kill -TERM \"\$p\" 2>/dev/null'" >"$tmp_out" 2>/dev/null
rc=$?
set -e
out="$(cat "$tmp_out")"
stopped_state=0
printf '%s\n' "$out" | grep -q 'Stopped' && stopped_state=1
echo "JM:023:rc=$rc stopped_state=$stopped_state"
