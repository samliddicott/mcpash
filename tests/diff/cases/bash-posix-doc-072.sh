#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 72: unset -v readonly should be fatal in non-interactive shell.
ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${MCTASH_MODE-}" ]]; then
  runner_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  runner_cmd="bash --posix"
fi
tmp_out="$(mktemp)"
trap 'rm -f "$tmp_out"' EXIT
set +e
eval "${runner_cmd} -c 'readonly V072=1; unset -v V072; echo CONT'" >"$tmp_out" 2>/dev/null
rc=$?
out="$(cat "$tmp_out")"
set -e
nz=0
[ "$rc" -ne 0 ] && nz=1
cont=0
printf '%s\n' "$out" | grep -q '^CONT$' && cont=1
echo "JM:072:nz=$nz cont=$cont"
