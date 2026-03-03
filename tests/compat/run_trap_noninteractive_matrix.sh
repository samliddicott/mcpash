#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRICT="${STRICT:-0}"

signals=(HUP INT QUIT TERM USR1 USR2 ALRM PIPE)
fail=0

run_shell() {
  local shell_cmd="$1"
  local src="$2"
  local out="$3"
  local -a cmd_arr=()
  read -r -a cmd_arr <<<"$shell_cmd"
  set +e
  "${cmd_arr[@]}" -c "$src" >"$out" 2>&1
  local rc=$?
  set -e
  echo "$rc"
}

for sig in "${signals[@]}"; do
  src="trap 'echo TM:GOT:$sig' $sig; kill -$sig \$\$; echo TM:END"
  ash_out="$(mktemp)"
  m_out="$(mktemp)"
  ash_rc="$(run_shell "ash" "$src" "$ash_out")"
  set +e
  PYTHONPATH="$ROOT/src" python3 -m mctash --posix -c "$src" >"$m_out" 2>&1
  m_rc=$?
  set -e
  ash_m="$(grep '^TM:' "$ash_out" || true)"
  m_m="$(grep '^TM:' "$m_out" || true)"
  echo "=== trap-nonint:${sig} ==="
  echo "  ash rc=${ash_rc} mctash rc=${m_rc}"
  echo "  ash: ${ash_m}"
  echo "  mct: ${m_m}"
  rm -f "$ash_out" "$m_out"
  if [[ "$STRICT" == "1" ]]; then
    [[ "$ash_rc" == "$m_rc" ]] || { echo "[FAIL] trap ${sig}: rc mismatch" >&2; fail=1; }
    [[ "$ash_m" == "$m_m" ]] || { echo "[FAIL] trap ${sig}: marker mismatch" >&2; fail=1; }
  fi
done

if [[ "$STRICT" != "1" ]]; then
  echo "[INFO] STRICT=0: non-interactive trap matrix is informational"
fi

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] trap non-interactive matrix"
  exit 1
fi
echo "[PASS] trap non-interactive matrix"
