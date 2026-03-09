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
eval "${runner_cmd} -c 'readonly R35=1; echo JM:035:pre; R35=2; echo JM:035:post'" >"$tmp_out" 2>/dev/null
rc=$?
out="$(cat "$tmp_out")"
set -e

nz=0
[ "$rc" -ne 0 ] && nz=1

post=0
printf '%s\n' "$out" | grep -q '^JM:035:post$' && post=1

echo "JM:035:nz=$nz post=$post"
