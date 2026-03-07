#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 58: kill should reject SIG-prefixed names in POSIX mode
set +e
kill -SIGTERM $$ >/dev/null 2>&1
st=$?
set -e
echo JM:058:${st}

