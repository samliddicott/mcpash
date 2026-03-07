#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"

if [[ -n "${BASH_VERSION-}" ]]; then
  self_shell_cmd='bash --posix'
else
  self_shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
(
  cd "$tmp"
  : > a
  : > b
  f='*'
  : > $f
  [[ -e "*" ]] && echo 'JM:009:1' || echo 'JM:009:0'
)
