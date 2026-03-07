#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 51: xpg_echo behavior
shopt -s xpg_echo 2>/dev/null || true
echo "JM:051:$(echo -n \tX | od -An -tx1 | tr -d ' 
')"

