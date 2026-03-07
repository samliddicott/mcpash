#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 52: export/readonly output format
unset E52
E52=ok
exp52="$(export -p | grep -E 'E52=ok' | head -n1 || true)"
readonly R52=rv
ro52="$(readonly -p | grep -E 'R52=' | head -n1 || true)"
printf 'JM:052:exp:%s
' "$([[ -n "$exp52" ]] && echo 1 || echo 0)"
printf 'JM:052:ro:%s
' "$([[ -n "$ro52" ]] && echo 1 || echo 0)"

