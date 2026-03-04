#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${ROOT}/tests/bash/upstream"
BRANCH="${BASH_UPSTREAM_BRANCH:-master}"
INDEX_URL="https://git.savannah.gnu.org/cgit/bash.git/tree/tests?h=${BRANCH}"
README_URL="https://git.savannah.gnu.org/cgit/bash.git/plain/tests/README?h=${BRANCH}"
COPYRIGHT_URL="https://git.savannah.gnu.org/cgit/bash.git/plain/tests/COPYRIGHT?h=${BRANCH}"
MANIFEST="${OUT_DIR}/manifest-${BRANCH}.txt"

mkdir -p "$OUT_DIR"

wget -q -O "${OUT_DIR}/tree-${BRANCH}.html" "$INDEX_URL"
wget -q -O "${OUT_DIR}/README" "$README_URL"
wget -q -O "${OUT_DIR}/COPYRIGHT" "$COPYRIGHT_URL"

rg -o "tests/[A-Za-z0-9_.+-]+\\.tests" "${OUT_DIR}/tree-${BRANCH}.html" | sort -u > "$MANIFEST"

echo "[INFO] branch: ${BRANCH}"
echo "[INFO] wrote: ${OUT_DIR}/tree-${BRANCH}.html"
echo "[INFO] wrote: ${OUT_DIR}/README"
echo "[INFO] wrote: ${OUT_DIR}/COPYRIGHT"
echo "[INFO] wrote manifest: ${MANIFEST} ($(wc -l < "$MANIFEST" | tr -d ' ') test files)"
