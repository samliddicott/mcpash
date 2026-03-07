#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"

if [[ -n "${BASH_VERSION-}" ]]; then
  self_shell_cmd='bash --posix'
else
  self_shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
fi

out="$( { echo $(bp5); } 2>/dev/null )"
alias bp5='echo LATE'
if [[ -z "$out" ]]; then echo 'JM:005:empty'; else echo "JM:005:${out}"; fi
