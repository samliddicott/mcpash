#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${MCTASH_MODE-}" ]]; then
  runner_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  runner_cmd="bash --posix"
fi

tmp_out="$(mktemp)"
trap '/bin/rm -f "$tmp_out"' EXIT
set +e
eval "${runner_cmd} -c 'readonly R36=1; R36=2 true || true; echo JM:036:after_true; R36=3 export Y36=1; echo JM:036:after_export'" >"$tmp_out" 2>/dev/null
rc=$?
out="$(cat "$tmp_out")"
set -e

nz=0
[ "$rc" -ne 0 ] && nz=1

after_true=0
printf '%s\n' "$out" | grep -q '^JM:036:after_true$' && after_true=1
after_export=0
printf '%s\n' "$out" | grep -q '^JM:036:after_export$' && after_export=1
echo "JM:036:nz=$nz after_true=$after_true after_export=$after_export"
