#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME="$ROOT/src/mctash/runtime.py"
ALLOWLIST="$ROOT/tests/regressions/asdl_fallback_allowlist.txt"

mapfile -t found < <(
  rg --no-filename --no-line-number "_expand_assignment_word\(self\._asdl_word_to_text\(word\)\)|_expand_argv\(\[Word\(self\._asdl_word_to_text\(word\)\)\]\)|_expand_asdl_word_fields_or_legacy" "$RUNTIME" \
    | sed 's/^[[:space:]]*//'
)
mapfile -t allowed < <(sed '/^\s*$/d' "$ALLOWLIST")

if [[ "${#found[@]}" -ne "${#allowed[@]}" ]]; then
  echo "[FAIL] ASDL fallback audit: fallback count changed (${#found[@]} found, ${#allowed[@]} allowed)" >&2
  printf '  found:\n' >&2
  printf '    %s\n' "${found[@]:-<none>}" >&2
  exit 1
fi

for i in "${!allowed[@]}"; do
  if [[ "${found[$i]}" != "${allowed[$i]}" ]]; then
    echo "[FAIL] ASDL fallback audit: unexpected fallback line" >&2
    echo "  expected: ${allowed[$i]}" >&2
    echo "  found:    ${found[$i]}" >&2
    exit 1
  fi
done

echo "[PASS] asdl_fallback_audit"
