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
eval 'export(){ echo FUNC18; }' >/dev/null 2>&1
set -e
type export | sed -n '1p' | sed 's/[[:space:]]\+/ /g;s/^ *//;s/ *$//' | sed 's/^/JM:018:/' 
