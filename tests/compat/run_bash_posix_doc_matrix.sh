#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="${ROOT}/tests/diff/run.sh"
MATRIX="${ROOT}/docs/specs/bash-posix-mode-implementation-matrix.tsv"
REPORT="${ROOT}/docs/reports/bash-posix-doc-matrix-latest.md"
LOGDIR="${ROOT}/tests/diff/logs/bash-posix-doc"
STRICT="${STRICT:-0}"
ITEM_MAX="${ITEM_MAX:-10}"

if [[ ! -f "$MATRIX" ]]; then
  echo "missing matrix file: $MATRIX" >&2
  exit 2
fi

mapfile -t CASES < <(
  awk -F'\t' -v max="${ITEM_MAX}" '
    NR > 1 && $1 ~ /^BPOSIX\.CORE\./ && ($4 + 0) >= 1 && ($4 + 0) <= max && $11 != "" { print $11 }
  ' "$MATRIX" | sort -u
)

if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "no case files mapped for BPOSIX.CORE.001..${ITEM_MAX}" >&2
  exit 2
fi

mkdir -p "$LOGDIR"
runner_out="$LOGDIR/runner.out"

set +e
env PARITY_MIRROR_POSIX=1 MCTASH_DIAG_STYLE=bash "$RUNNER" --logdir "$LOGDIR" "${CASES[@]}" >"$runner_out" 2>&1
rc=$?
set -e

mismatch_file="$LOGDIR/mismatches.txt"
rg -n "mismatch" "$runner_out" > "$mismatch_file" || true
mismatch_count=$(wc -l < "$mismatch_file" | tr -d ' ')

covered=$(awk -F'\t' -v max="${ITEM_MAX}" 'NR>1 && $1 ~ /^BPOSIX\.CORE\./ && ($4+0)<=max && $9=="covered" && $10=="covered" {n++} END{print n+0}' "$MATRIX")
partial=$(awk -F'\t' -v max="${ITEM_MAX}" 'NR>1 && $1 ~ /^BPOSIX\.CORE\./ && ($4+0)<=max && ($9!="covered" || $10!="covered") {n++} END{print n+0}' "$MATRIX")

now="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
{
  echo "# Bash POSIX Doc Matrix"
  echo
  echo "Generated: ${now}"
  echo
  echo "Source: https://tiswww.case.edu/php/chet/bash/POSIX (6.11.2)"
  echo
  echo "## Tranche Summary (Items 1..${ITEM_MAX})"
  echo
  echo "- covered rows: ${covered}"
  echo "- partial rows: ${partial}"
  echo "- executed case files: ${#CASES[@]}"
  echo "- diff runner exit code: ${rc}"
  echo "- mismatch lines: ${mismatch_count}"
  echo
  echo "## Executed Cases"
  echo
  for c in "${CASES[@]}"; do
    echo "- ${c}"
  done
  echo
  echo "## Partial Rows in Tranche"
  echo
  awk -F'\t' -v max="${ITEM_MAX}" '
    NR>1 && $1 ~ /^BPOSIX\.CORE\./ && ($4+0)<=max && ($9!="covered" || $10!="covered") {
      printf "- %s (item %s): %s\n", $1, $4, $12
    }
  ' "$MATRIX"
  echo
  echo "## Mismatch Extract"
  echo
  if [[ "$mismatch_count" -eq 0 ]]; then
    echo "- none"
  else
    sed 's#^#- #' "$mismatch_file"
  fi
} > "$REPORT"

echo "[INFO] wrote $REPORT"
if [[ "$STRICT" == "1" && "$rc" -ne 0 ]]; then
  echo "[FAIL] bash posix doc matrix" >&2
  exit "$rc"
fi
echo "[PASS] bash posix doc matrix (strict=${STRICT})"
