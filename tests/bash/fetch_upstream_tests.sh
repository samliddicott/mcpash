#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${ROOT}/tests/bash/upstream"
REF="${BASH_UPSTREAM_REF:-${BASH_UPSTREAM_BRANCH:-master}}"
FORCE_REFRESH="${FORCE_REFRESH:-0}"
WGET_OPTS_DEFAULT=(--timeout=20 --tries=2 --retry-connrefused --waitretry=1)
WGET_OPTS=("${WGET_OPTS_DEFAULT[@]}")

if [[ "${1:-}" == "--refresh" ]]; then
  FORCE_REFRESH=1
fi

safe_ref="$(printf '%s' "$REF" | sed 's/[^A-Za-z0-9._-]/_/g')"
REF_DIR="${OUT_DIR}/${safe_ref}"
INDEX_URL="https://git.savannah.gnu.org/cgit/bash.git/tree/tests?h=${REF}"
README_URL="https://git.savannah.gnu.org/cgit/bash.git/plain/tests/README?h=${REF}"
COPYRIGHT_URL="https://git.savannah.gnu.org/cgit/bash.git/plain/tests/COPYRIGHT?h=${REF}"
TREE_HTML="${REF_DIR}/tree.html"
README_TXT="${REF_DIR}/README"
COPYRIGHT_TXT="${REF_DIR}/COPYRIGHT"
MANIFEST="${REF_DIR}/manifest.txt"
LOCK_FILE="${REF_DIR}/fetch-lock.json"
LATEST_LINK="${OUT_DIR}/latest"

mkdir -p "$REF_DIR"

fetch() {
  local url="$1"
  local out="$2"
  local tmp="${out}.tmp.$$"
  rm -f "$tmp"
  if ! wget -q "${WGET_OPTS[@]}" -O "$tmp" "$url"; then
    rm -f "$tmp"
    return 1
  fi
  mv -f "$tmp" "$out"
}

cache_ready=0
if [[ "$FORCE_REFRESH" != "1" && -f "$LOCK_FILE" && -f "$TREE_HTML" && -f "$README_TXT" && -f "$COPYRIGHT_TXT" && -f "$MANIFEST" ]]; then
  cache_ready=1
fi

if [[ "$cache_ready" == "1" ]]; then
  echo "[INFO] cache hit for ref=${REF} (${REF_DIR})"
else
  fetch "$INDEX_URL" "${TREE_HTML}"
  fetch "$README_URL" "${README_TXT}"
  fetch "$COPYRIGHT_URL" "${COPYRIGHT_TXT}"
  rg -o "tests/[A-Za-z0-9_.+-]+\\.tests" "${TREE_HTML}" | sort -u > "$MANIFEST"
fi

test_count="$(wc -l < "$MANIFEST" | tr -d ' ')"
fetched_at="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
cat > "$LOCK_FILE" <<EOF
{
  "ref": "${REF}",
  "safe_ref": "${safe_ref}",
  "fetched_at_utc": "${fetched_at}",
  "test_manifest_count": ${test_count},
  "cache_hit": ${cache_ready},
  "index_url": "${INDEX_URL}",
  "readme_url": "${README_URL}",
  "copyright_url": "${COPYRIGHT_URL}",
  "manifest_path": "tests/bash/upstream/${safe_ref}/manifest.txt"
}
EOF

ln -sfn "$safe_ref" "$LATEST_LINK"

echo "[INFO] ref: ${REF}"
echo "[INFO] ref dir: ${REF_DIR}"
echo "[INFO] tree: ${TREE_HTML}"
echo "[INFO] readme: ${README_TXT}"
echo "[INFO] copyright: ${COPYRIGHT_TXT}"
echo "[INFO] manifest: ${MANIFEST} (${test_count} test files)"
echo "[INFO] lock: ${LOCK_FILE}"
echo "[INFO] latest link: ${LATEST_LINK} -> ${safe_ref}"
