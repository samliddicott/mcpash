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
eval 'a/b(){ echo BAD; }' >/dev/null 2>&1
stdef=$?
a/b >/dev/null 2>&1
strun=$?
set -e
echo "JM:019:def=${stdef}:run=${strun}"
