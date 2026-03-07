#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 50: PATH_MAX fallback behavior is platform-sensitive; probe status shape
set +e
cd / >/dev/null 2>&1
st=$?
set -e
echo JM:050:${st}

