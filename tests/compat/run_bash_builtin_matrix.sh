#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="$ROOT/tests/diff/run.sh"
LOGDIR="$ROOT/tests/diff/logs/bash-builtin-matrix"
REPORT="$ROOT/docs/reports/bash-builtin-matrix-latest.md"
STRICT="${STRICT:-0}"
ROW_TIMEOUT="${ROW_TIMEOUT:-120}"
MCTASH_MAX_VMEM_KB="${MCTASH_MAX_VMEM_KB:-786432}"

mkdir -p "$LOGDIR"

run_lane() {
  local lane="$1"
  shift
  local out="$LOGDIR/${lane}.out"
  local rc=0
  set +e
  timeout -k 5 "$ROW_TIMEOUT" \
    env MCTASH_DIAG_STYLE=bash \
      MCTASH_CMD="env MCTASH_MAX_VMEM_KB=${MCTASH_MAX_VMEM_KB} PYTHONPATH=${ROOT}/src python3 -m mctash" \
      "$RUNNER" --logdir "$LOGDIR/$lane" "$@" >"$out" 2>&1
  rc=$?
  set -e
  echo "$rc" > "$LOGDIR/${lane}.rc"
  return 0
}

core_cases=(
  bash-builtin-declare-typeset-local
  bash-builtin-enable
  bash-builtin-help
  bash-builtin-dirstack
  bash-builtin-disown
  bash-builtin-completion
)

run_lane core "${core_cases[@]}"

set +e
timeout -k 5 "$ROW_TIMEOUT" \
  env PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 MCTASH_DIAG_STYLE=bash \
    MCTASH_CMD="env MCTASH_MAX_VMEM_KB=${MCTASH_MAX_VMEM_KB} PYTHONPATH=${ROOT}/src python3 -m mctash" \
    "$RUNNER" --logdir "$LOGDIR/bash_compat" bash-compat-mapfile-readarray >"$LOGDIR/bash_compat.out" 2>&1
compat_rc=$?
set -e
echo "$compat_rc" > "$LOGDIR/bash_compat.rc"

interactive_rc=0
if [[ "$STRICT" == "1" ]]; then
  set +e
  timeout -k 5 "$ROW_TIMEOUT" "$ROOT/tests/compat/run_completion_interactive_matrix.sh" >"$LOGDIR/interactive.out" 2>&1
  interactive_rc=$?
  set -e
fi
echo "$interactive_rc" > "$LOGDIR/interactive.rc"

core_rc="$(cat "$LOGDIR/core.rc")"
overall=0
[[ "$core_rc" -eq 0 ]] || overall=1
[[ "$compat_rc" -eq 0 ]] || overall=1
if [[ "$STRICT" == "1" && "$interactive_rc" -ne 0 ]]; then
  overall=1
fi

now="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
{
  echo "# Bash Builtin Matrix"
  echo
  echo "Generated: $now"
  echo
  echo "## Summary"
  echo
  echo "- core lane rc: $core_rc"
  echo "- bash-compat lane rc: $compat_rc"
  echo "- interactive lane rc: $interactive_rc (STRICT=$STRICT)"
  echo "- overall rc: $overall"
  echo "- memory cap (KB): $MCTASH_MAX_VMEM_KB"
  echo "- row timeout (s): $ROW_TIMEOUT"
  echo
  echo "## Core Cases"
  echo
  for c in "${core_cases[@]}"; do
    echo "- ${c}.sh"
  done
  echo
  echo "## Bash-Compat Cases"
  echo
  echo "- bash-compat-mapfile-readarray.sh"
} > "$REPORT"

echo "[INFO] wrote $REPORT"
if [[ "$overall" -ne 0 ]]; then
  echo "[FAIL] bash builtin matrix" >&2
  exit 1
fi

echo "[PASS] bash builtin matrix"
