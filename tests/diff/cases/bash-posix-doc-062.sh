#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 62: read interrupted by trapped signal returns >128
set +e
trap 'echo TRAP62 >/dev/null' INT
( sleep 0.2; kill -INT $$ ) &
read v62
st=$?
set -e
echo JM:062:${st}

