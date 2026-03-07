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
  timeout 12s script -qec "$cmd" /dev/null | tr -d '\r' >"$out"
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
  local bash_cmd="$2"
  local mctash_cmd="$3"
  local b_rc m_rc
  b_rc="$(run_pty_case "${label}.bash" "$bash_cmd")"
  m_rc="$(run_pty_case "${label}.mctash" "$mctash_cmd")"
  local b_m="$tmpdir/${label}.bash.markers"
  local m_m="$tmpdir/${label}.mctash.markers"
  extract_markers "$tmpdir/${label}.bash.out" >"$b_m"
  extract_markers "$tmpdir/${label}.mctash.out" >"$m_m"
  echo "=== jobs-tty:${label} ==="
  echo "  bash rc=${b_rc} mctash rc=${m_rc}"
  sed 's/^/  bash: /' "$b_m"
  sed 's/^/  mct: /' "$m_m"
  if [[ "$STRICT" == "1" ]]; then
    if [[ "$b_rc" -ne "$m_rc" ]]; then
      echo "[FAIL] jobs-tty ${label}: rc mismatch" >&2
      fail=1
    fi
    if ! diff -u "$b_m" "$m_m" >/dev/null; then
      echo "[FAIL] jobs-tty ${label}: marker mismatch" >&2
      fail=1
    fi
  fi
}

bash_ttin="bash --posix -i -c \"set +H; set -m; cat </dev/tty & for i in 1 2 3 4 5 6 7 8 9 10; do jobs | grep -q 'Stopped(SIGTTIN)' && break; sleep 0.05; done; jobs | grep -q 'Stopped(SIGTTIN)'; echo JM:ttin:\\$?; kill -CONT %1 >/dev/null 2>&1 || true; kill %1 >/dev/null 2>&1 || true; wait %1 >/dev/null 2>&1 || true; echo JM:done\""
mct_ttin="cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i -c \"set +H; set -m; cat </dev/tty & for i in 1 2 3 4 5 6 7 8 9 10; do jobs | grep -q 'Stopped(SIGTTIN)' && break; sleep 0.05; done; jobs | grep -q 'Stopped(SIGTTIN)'; echo JM:ttin:\\$?; kill -CONT %1 >/dev/null 2>&1 || true; kill %1 >/dev/null 2>&1 || true; wait %1 >/dev/null 2>&1 || true; echo JM:done\""
check_pair "sigttin" "$bash_ttin" "$mct_ttin"

bash_ttou="bash --posix -i -c \"set +H; set -m; stty tostop; sh -c 'echo X >/dev/tty; sleep 1' & for i in 1 2 3 4 5 6 7 8 9 10; do jobs | grep -q 'Stopped(SIGTTOU)' && break; sleep 0.05; done; jobs | grep -q 'Stopped(SIGTTOU)'; echo JM:ttou:\\$?; stty -tostop; kill -CONT %1 >/dev/null 2>&1 || true; kill %1 >/dev/null 2>&1 || true; wait %1 >/dev/null 2>&1 || true; echo JM:done\""
mct_ttou="cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i -c \"set +H; set -m; stty tostop; sh -c 'echo X >/dev/tty; sleep 1' & for i in 1 2 3 4 5 6 7 8 9 10; do jobs | grep -q 'Stopped(SIGTTOU)' && break; sleep 0.05; done; jobs | grep -q 'Stopped(SIGTTOU)'; echo JM:ttou:\\$?; stty -tostop; kill -CONT %1 >/dev/null 2>&1 || true; kill %1 >/dev/null 2>&1 || true; wait %1 >/dev/null 2>&1 || true; echo JM:done\""
check_pair "sigttou" "$bash_ttou" "$mct_ttou"

if [[ "$STRICT" != "1" ]]; then
  echo "[INFO] STRICT=0: job tty stop matrix is informational"
fi

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] job tty stop matrix"
  exit 1
fi

echo "[PASS] job tty stop matrix"
