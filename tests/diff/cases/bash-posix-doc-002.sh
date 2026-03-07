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
printf 'echo __ENV_HIT__\n' >"${tmp}/envrc"
chmod 700 "${tmp}/envrc"
out="$(eval "ENV='${tmp}/envrc' HOME='${tmp}' ${self_shell_cmd} -i -c 'echo __CMD__'" 2>/dev/null | tr -d '\r')"
if [[ "$out" == *"__ENV_HIT__"* && "$out" == *"__CMD__"* ]]; then echo 'JM:002:1'; else echo 'JM:002:0'; fi
