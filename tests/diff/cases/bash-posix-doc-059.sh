#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 59: kill fails if any arg invalid in POSIX mode
set +e
kill -TERM $$ 999999 >/dev/null 2>&1
st=$?
set -e
echo JM:059:${st}

