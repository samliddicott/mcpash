#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 56: fc -s too many args returns failure
set +e
fc -s a b c >/tmp/fc56.out 2>/tmp/fc56.err
st=$?
set -e
echo JM:056:${st}
rm -f /tmp/fc56.out /tmp/fc56.err

