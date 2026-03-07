#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 54: default fc editor is ed
set +e
unset FCEDIT EDITOR VISUAL
fc -e - -1 >/tmp/fc54.out 2>/tmp/fc54.err
st=$?
set -e
echo JM:054:${st}
rm -f /tmp/fc54.out /tmp/fc54.err

