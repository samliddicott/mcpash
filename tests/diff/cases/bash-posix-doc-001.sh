#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"

if [[ -n "${MCTASH_MODE-}" ]]; then
  self_shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  self_shell_cmd='bash --posix'
fi

echo "JM:001:$([[ -n "${POSIXLY_CORRECT-}" ]] && echo 1 || echo 0)"
