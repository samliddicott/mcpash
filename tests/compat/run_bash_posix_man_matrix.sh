#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="${ROOT}/tests/diff/run.sh"
COVERAGE="${ROOT}/tests/compat/bash_posix_man_coverage.tsv"
REPORT="${ROOT}/docs/reports/bash-posix-man-matrix-latest.md"
LOGDIR="${ROOT}/tests/diff/logs/bash-posix-man"

if [[ ! -f "$COVERAGE" ]]; then
  echo "missing coverage file: $COVERAGE" >&2
  exit 2
fi

mapfile -t CASES < <(awk -F'\t' '($0 !~ /^#/ && $2=="covered" && $3!="") {print $3}' "$COVERAGE" | sort -u)
EXTRA_CASES=(
  man-bash-posix-13-exec-errors-signals-jobs
  man-bash-posix-14-env-exec-flow
)
for ec in "${EXTRA_CASES[@]}"; do
  CASES+=("$ec")
done
mapfile -t CASES < <(printf '%s\n' "${CASES[@]}" | awk 'NF' | sort -u)
if [[ ${#CASES[@]} -eq 0 ]]; then
  echo "no covered cases mapped in $COVERAGE" >&2
  exit 2
fi

mkdir -p "$LOGDIR"
runner_out="$LOGDIR/runner.out"
set +e
env PARITY_MIRROR_POSIX=1 MCTASH_DIAG_STYLE=bash BASH_BIN='bash --posix' "$RUNNER" --logdir "$LOGDIR" "${CASES[@]}" >"$runner_out" 2>&1
rc=$?
set -e

covered=$(awk -F'\t' '($0 !~ /^#/ && $2=="covered") {n++} END {print n+0}' "$COVERAGE")
partial=$(awk -F'\t' '($0 !~ /^#/ && $2=="partial") {n++} END {print n+0}' "$COVERAGE")
out_scope=$(awk -F'\t' '($0 !~ /^#/ && $2=="out_of_scope") {n++} END {print n+0}' "$COVERAGE")

mismatch_file="$LOGDIR/mismatches.txt"
rg -n "mismatch" "$runner_out" > "$mismatch_file" || true
mismatch_count=$(wc -l < "$mismatch_file" | tr -d ' ')

now="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
{
  echo "# Bash POSIX Man-Page Matrix"
  echo
  echo "Generated: ${now}"
  echo
  echo "## Summary"
  echo
  echo "- covered builtins: ${covered}"
  echo "- partial builtins: ${partial}"
  echo "- out-of-scope builtins: ${out_scope}"
  echo "- executed case files: ${#CASES[@]}"
  echo "- matrix exit code: ${rc}"
  echo "- mismatch lines detected: ${mismatch_count}"
  echo
  echo "## Executed Cases"
  echo
  for c in "${CASES[@]}"; do
    echo "- ${c}.sh"
  done
  echo
  echo "## Partial/Uncovered Builtins"
  echo
  awk -F'\t' '($0 !~ /^#/ && $2=="partial") {printf "- %s: %s\n", $1, $4}' "$COVERAGE"
  echo
  echo "## Out of Scope for POSIX Parity Lane"
  echo
  awk -F'\t' '($0 !~ /^#/ && $2=="out_of_scope") {printf "- %s: %s\n", $1, $4}' "$COVERAGE"
  echo
  echo "## Mismatch Extract"
  echo
  if [[ "$mismatch_count" -eq 0 ]]; then
    echo "- none"
  else
    sed 's#^#- #' "$mismatch_file"
    echo
    echo "## Runner Output"
    echo
    sed 's#^#    #' "$runner_out"
  fi
} > "$REPORT"

echo "[INFO] wrote $REPORT"
if [[ "$rc" -ne 0 ]]; then
  echo "[FAIL] bash posix man matrix" >&2
  exit "$rc"
fi
echo "[PASS] bash posix man matrix"
