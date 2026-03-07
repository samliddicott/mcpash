#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 55: fc extra args error
set +e
fc 1 2 3 >/tmp/fc55.out 2>/tmp/fc55.err
st=$?
set -e
echo JM:055:${st}
rm -f /tmp/fc55.out /tmp/fc55.err

