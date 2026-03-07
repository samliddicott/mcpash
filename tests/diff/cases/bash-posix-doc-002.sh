#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
printf 'echo __ENV_HIT__\n' >"${tmp}/envrc"
chmod 700 "${tmp}/envrc"
if [[ -n "${MCTASH_MODE-}" ]]; then
  out="$(ENV="${tmp}/envrc" HOME="${tmp}" PYTHONPATH="${ROOT_DIR}/src" python3 -m mctash --posix -i -c 'echo __CMD__' 2>/dev/null | tr -d '\r')"
else
  out="$(ENV="${tmp}/envrc" HOME="${tmp}" bash --posix -i -c 'echo __CMD__' 2>/dev/null | tr -d '\r')"
fi
if printf '%s\n' "$out" | grep -q "__ENV_HIT__" && printf '%s\n' "$out" | grep -q "__CMD__"; then
  echo 'JM:002:1'
else
  echo 'JM:002:0'
fi
