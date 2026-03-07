#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 64: `set` variable formatting/quoting behavior.
V064_SIMPLE=abc
V064_SPACE='a b'
V064_META='a*b'
line_simple="$(set | grep '^V064_SIMPLE=' | head -n1 || true)"
line_space="$(set | grep '^V064_SPACE=' | head -n1 || true)"
line_meta="$(set | grep '^V064_META=' | head -n1 || true)"
printf 'JM:064:S:%s\n' "$line_simple"
printf 'JM:064:SP:%s\n' "$line_space"
printf 'JM:064:M:%s\n' "$line_meta"
