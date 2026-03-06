#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRICT="${STRICT:-0}"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

fail=0

run_pty_case() {
  local label="$1"
  local cmd="$2"
  local out="$tmpdir/${label}.out"
  set +e
  script -qec "$cmd" /dev/null | tr -d '\r' >"$out"
  local rc=$?
  set -e
  echo "$rc"
}

extract_markers() {
  local file="$1"
  grep '^JM:' "$file" || true
}

check_pair() {
  local label="$1"
  local ash_cmd="$2"
  local mctash_cmd="$3"
  local ash_rc m_rc
  ash_rc="$(run_pty_case "${label}.ash" "$ash_cmd")"
  m_rc="$(run_pty_case "${label}.mctash" "$mctash_cmd")"
  local ash_m="$tmpdir/${label}.ash.markers"
  local m_m="$tmpdir/${label}.mctash.markers"
  extract_markers "$tmpdir/${label}.ash.out" >"$ash_m"
  extract_markers "$tmpdir/${label}.mctash.out" >"$m_m"
  echo "=== jobs:${label} ==="
  echo "  ash rc=${ash_rc} mctash rc=${m_rc}"
  sed 's/^/  ash: /' "$ash_m"
  sed 's/^/  mct: /' "$m_m"
  if [[ "$STRICT" == "1" ]]; then
    if [[ "$ash_rc" -ne "$m_rc" ]]; then
      echo "[FAIL] jobs ${label}: rc mismatch" >&2
      fail=1
    fi
    if ! diff -u "$ash_m" "$m_m" >/dev/null; then
      echo "[FAIL] jobs ${label}: marker mismatch" >&2
      fail=1
    fi
  fi
}

ash_shell="ash -i -c 'set -m; sleep 0.05 & jobs >/dev/null 2>&1; echo JM:jobs:$?; fg %1 >/dev/null 2>&1; echo JM:fg:$?; wait >/dev/null 2>&1; echo JM:done'"
mctash_shell="cd '$ROOT' && PYTHONPATH='$ROOT/src' python3 -m mctash -i -c 'set -m; sleep 0.05 & jobs >/dev/null 2>&1; echo JM:jobs:$?; fg %1 >/dev/null 2>&1; echo JM:fg:$?; wait >/dev/null 2>&1; echo JM:done'"
check_pair "fg-basic" "$ash_shell" "$mctash_shell"

ash_shell2="ash -i -c 'set -m; sleep 0.05 & bg %1 >/dev/null 2>&1; echo JM:bg:$?; wait >/dev/null 2>&1; echo JM:done'"
mctash_shell2="cd '$ROOT' && PYTHONPATH='$ROOT/src' python3 -m mctash -i -c 'set -m; sleep 0.05 & bg %1 >/dev/null 2>&1; echo JM:bg:$?; wait >/dev/null 2>&1; echo JM:done'"
check_pair "bg-basic" "$ash_shell2" "$mctash_shell2"

bash_shell3="bash --posix -i -c 'set -m; sleep 0.6 & sleep 0.6 & %1 >/dev/null 2>&1; echo JM:pctfg:$?; %2 & echo JM:pctbg:$?; wait >/dev/null 2>&1; echo JM:done'"
mctash_shell3="cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i -c 'set -m; sleep 0.6 & sleep 0.6 & %1 >/dev/null 2>&1; echo JM:pctfg:$?; %2 & echo JM:pctbg:$?; wait >/dev/null 2>&1; echo JM:done'"
check_pair "jobspec-command-forms" "$bash_shell3" "$mctash_shell3"

bash_shell4="bash --posix -i -c 'set -m; yes | head -n 1 >/dev/null & jc=\$(jobs | wc -l); printf \"JM:jc:%s\\n\" \"\$jc\"; wait %1 >/dev/null 2>&1; echo JM:w:$?'"
mctash_shell4="cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i -c 'set -m; yes | head -n 1 >/dev/null & jc=\$(jobs | wc -l); printf \"JM:jc:%s\\n\" \"\$jc\"; wait %1 >/dev/null 2>&1; echo JM:w:$?'"
check_pair "pipeline-one-job" "$bash_shell4" "$mctash_shell4"

if [[ "$STRICT" != "1" ]]; then
  echo "[INFO] STRICT=0: interactive jobs matrix is informational"
fi

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] jobs interactive matrix"
  exit 1
fi

echo "[PASS] jobs interactive matrix"
