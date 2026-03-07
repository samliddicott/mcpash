#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 49: logical cd should fail rather than fallback physical
TMP49="$(mktemp -d)"; trap 'rm -rf "$TMP49"' EXIT
mkdir -p "$TMP49/a" "$TMP49/b"
ln -s "$TMP49/a" "$TMP49/link"
cd "$TMP49/link"
rm -rf "$TMP49/a"
set +e
cd .. >/dev/null 2>&1
st=$?
set -e
echo JM:049:${st}

