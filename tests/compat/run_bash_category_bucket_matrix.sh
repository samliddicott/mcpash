#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT="$ROOT/docs/reports/bash-category-buckets-latest.md"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

run_step() {
  local id="$1"
  local name="$2"
  local cmd="$3"
  local out="$TMPDIR/${id}.out"
  set +e
  bash -lc "$cmd" >"$out" 2>&1
  local rc=$?
  set -e
  if [[ "$rc" -eq 0 ]]; then
    echo "$id|$name|covered|$cmd" >>"$TMPDIR/rows"
  else
    echo "$id|$name|partial|$cmd" >>"$TMPDIR/rows"
    echo "[$id] rc=$rc" >>"$TMPDIR/fail"
    sed -n '1,40p' "$out" >>"$TMPDIR/fail"
    echo >>"$TMPDIR/fail"
  fi
}

: >"$TMPDIR/rows"
: >"$TMPDIR/fail"

run_step 1 "Invocation/startup/mode" "$ROOT/tests/compat/run_startup_mode_matrix.sh"
run_step 2 "Grammar/parser" "$ROOT/tests/diff/run.sh --case man-ash-grammar-negative --case man-ash-grammar-reserved --case man-ash-grammar-word-matrix --case man-ash-prefix-suffix"
run_step 3 "Expansion engine" "$ROOT/tests/diff/run.sh --case man-ash-var-ops --case man-ash-var-ops-matrix --case man-ash-word-nesting --case man-ash-word-nesting-matrix --case man-ash-glob-matrix --case man-ash-glob-full-matrix"
run_step 4 "Redirection/FD" "$ROOT/tests/diff/run.sh --case man-ash-redir --case man-ash-heredoc-edges --case man-ash-redir-heredoc-matrix"
run_step 5 "Builtins" "STRICT=1 $ROOT/tests/compat/run_bash_builtin_matrix.sh"
run_step 6 "Variables/state" "MCTASH_DIAG_STYLE=bash PARITY_MIRROR_POSIX=1 $ROOT/tests/diff/run.sh --case man-bash-posix-01-core-state --case man-bash-posix-14-env-exec-flow"
run_step 7 "Interactive UX" "$ROOT/tests/compat/run_completion_interactive_matrix.sh && $ROOT/tests/compat/run_interactive_ux_matrix.sh"
run_step 8 "Jobs/traps/signals" "STRICT=1 $ROOT/tests/compat/run_jobs_interactive_matrix.sh && STRICT=1 $ROOT/tests/compat/run_trap_noninteractive_matrix.sh && STRICT=1 $ROOT/tests/compat/run_trap_interactive_matrix.sh"
run_step 9 "Compatibility/restricted" "$ROOT/tests/compat/run_startup_mode_matrix.sh"

now="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
{
  echo "# Bash Category Buckets Matrix"
  echo
  echo "Generated: $now"
  echo
  echo "| Bucket | Name | Status | Gate |"
  echo "|---|---|---|---|"
  while IFS='|' read -r id name status gate; do
    echo "| $id | $name | $status | \`$gate\` |"
  done <"$TMPDIR/rows"
  echo
  if [[ -s "$TMPDIR/fail" ]]; then
    echo "## Failures"
    echo
    sed 's/^/    /' "$TMPDIR/fail"
  fi
} >"$REPORT"

echo "[INFO] wrote $REPORT"
if grep -q '| partial |' "$REPORT"; then
  echo "[FAIL] category bucket matrix has partial rows" >&2
  exit 1
fi

echo "[PASS] category bucket matrix"
