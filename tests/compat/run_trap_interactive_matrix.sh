#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRICT="${STRICT:-0}"
fail=0

run_pty() {
  local label="$1"
  local cmd="$2"
  local out="$3"
  set +e
  script -qec "$cmd" /dev/null | tr -d '\r' >"$out"
  local rc=$?
  set -e
  echo "$rc"
}

check_sig() {
  local sig="$1"
  local ash_cmd="ash -i -c 'trap \"echo IT:GOT:$sig\" $sig; kill -$sig \$\$; echo IT:END'"
  local m_cmd="cd '$ROOT' && PYTHONPATH='$ROOT/src' python3 -m mctash -i -c 'trap \"echo IT:GOT:$sig\" $sig; kill -$sig \$\$; echo IT:END'"
  local ao="$(mktemp)"
  local mo="$(mktemp)"
  local arc mrc
  arc="$(run_pty "ash.${sig}" "$ash_cmd" "$ao")"
  mrc="$(run_pty "mct.${sig}" "$m_cmd" "$mo")"
  local am mm
  am="$(grep '^IT:' "$ao" || true)"
  mm="$(grep '^IT:' "$mo" || true)"
  echo "=== trap-int:${sig} ==="
  echo "  ash rc=${arc} mctash rc=${mrc}"
  echo "  ash: ${am}"
  echo "  mct: ${mm}"
  rm -f "$ao" "$mo"
  if [[ "$STRICT" == "1" ]]; then
    [[ "$arc" == "$mrc" ]] || { echo "[FAIL] trap-int ${sig}: rc mismatch" >&2; fail=1; }
    [[ "$am" == "$mm" ]] || { echo "[FAIL] trap-int ${sig}: marker mismatch" >&2; fail=1; }
  fi
}

check_sig INT
check_sig TERM

if [[ "$STRICT" != "1" ]]; then
  echo "[INFO] STRICT=0: interactive trap matrix is informational"
fi

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] trap interactive matrix"
  exit 1
fi
echo "[PASS] trap interactive matrix"
