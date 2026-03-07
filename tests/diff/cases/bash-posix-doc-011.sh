#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${BASH_VERSION-}" ]]; then
  self_shell_cmd='bash --posix'
else
  self_shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
fi

set +e
out11="$(eval 'export(){ :; }' 2>&1)"
st11=$?
set -e
echo "JM:011:st=${st11}:err=$([[ -n "$out11" ]] && echo 1 || echo 0)"
