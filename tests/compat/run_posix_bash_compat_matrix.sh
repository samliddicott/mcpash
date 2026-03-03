#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MCTASH=(python3 -m mctash)
STRICT="${STRICT:-0}"
PARITY_COMPAT="${PARITY_COMPAT:-50}"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

fail=0

record() {
  local label="$1"
  local out="$2"
  echo "=== ${label} ==="
  sed 's/^/  /' "$out"
}

probe_pair_parity() {
  local label="$1"
  local script="$2"
  local bash_out="$tmpdir/${label}.bash.pair.out"
  local bash_err="$tmpdir/${label}.bash.pair.err"
  local m_out="$tmpdir/${label}.mctash.pair.out"
  local m_err="$tmpdir/${label}.mctash.pair.err"
  local bash_rc=0
  local m_rc=0

  set +e
  env BASH_COMPAT="$PARITY_COMPAT" bash --posix -c "$script" >"$bash_out" 2>"$bash_err"
  bash_rc=$?
  PYTHONPATH="$ROOT/src" env BASH_COMPAT="$PARITY_COMPAT" "${MCTASH[@]}" --posix -c "$script" >"$m_out" 2>"$m_err"
  m_rc=$?
  set -e

  echo "=== pair:${label} (compat=${PARITY_COMPAT}, posix=on) ==="
  echo "  bash rc=${bash_rc} mctash rc=${m_rc}"

  if [[ "$STRICT" == "1" ]]; then
    if [[ "$bash_rc" -ne "$m_rc" ]]; then
      echo "[FAIL] pair ${label}: rc mismatch bash=${bash_rc} mctash=${m_rc}" >&2
      fail=1
    fi
    if ! diff -u "$bash_out" "$m_out" >/dev/null; then
      echo "[FAIL] pair ${label}: stdout mismatch" >&2
      fail=1
    fi
    if ! diff -u "$bash_err" "$m_err" >/dev/null; then
      echo "[FAIL] pair ${label}: stderr mismatch" >&2
      fail=1
    fi
  fi
}

# Bash truth probes (hard assertions)
probe_bash() {
  local label="$1"
  shift
  local out="$tmpdir/${label}.bash.out"
  "$@" -c '
    set +e
    posix=$(set -o | sed -n "s/^posix[[:space:]]*//p")
    declare -a arr; s_arr=$?
    declare -A map; s_assoc=$?
    echo "posix=$posix arr=$s_arr assoc=$s_assoc compat=${BASH_COMPAT-<unset>}"
  ' >"$out" 2>&1
  record "bash:${label}" "$out"

  if ! grep -q 'arr=0' "$out"; then
    echo "[FAIL] bash ${label}: declare -a expected success" >&2
    fail=1
  fi
  if ! grep -q 'assoc=0' "$out"; then
    echo "[FAIL] bash ${label}: declare -A expected success" >&2
    fail=1
  fi
}

# mctash probes (soft assertions until feature lands; STRICT=1 to enforce)
probe_mctash() {
  local label="$1"
  local opts="$2"
  local compat="$3"
  local expect_arr="$4"
  local expect_assoc="$5"
  local out="$tmpdir/${label}.mctash.out"

  local rc=0
  local -a opt_argv=()
  if [[ -n "$opts" ]]; then
    # shellcheck disable=SC2206
    opt_argv=($opts)
  fi
  set +e
  if [[ -n "$compat" ]]; then
    PYTHONPATH="$ROOT/src" BASH_COMPAT="$compat" "${MCTASH[@]}" "${opt_argv[@]}" -c 'set +e; set -o | sed -n "s/^posix[[:space:]]*//p"; declare -a arr; echo "arr:$?"; declare -A map; echo "assoc:$?"' >"$out" 2>&1
    rc=$?
  else
    PYTHONPATH="$ROOT/src" "${MCTASH[@]}" "${opt_argv[@]}" -c 'set +e; set -o | sed -n "s/^posix[[:space:]]*//p"; declare -a arr; echo "arr:$?"; declare -A map; echo "assoc:$?"' >"$out" 2>&1
    rc=$?
  fi
  set -e

  record "mctash:${label} rc=${rc}" "$out"

  if grep -q "Traceback (most recent call last):" "$out"; then
    echo "[INFO] mctash ${label}: startup option path not yet hardened; captured traceback for now"
  fi

  if ! grep -q "^arr:${expect_arr}$" "$out"; then
    echo "[FAIL] mctash ${label}: expected arr:${expect_arr}" >&2
    fail=1
  fi
  if ! grep -q "^assoc:${expect_assoc}$" "$out"; then
    echo "[FAIL] mctash ${label}: expected assoc:${expect_assoc}" >&2
    fail=1
  fi

  if [[ "$STRICT" == "1" ]]; then
    echo "[INFO] mctash ${label}: strict mode active (expectations enforced)"
  fi
}

# Bash reference matrix
probe_bash plain bash
probe_bash posix bash --posix
probe_bash posix_compat env BASH_COMPAT="${PARITY_COMPAT}" bash --posix

# mctash progress matrix
probe_mctash plain "" "" 2 2
probe_mctash posix "--posix" "" 2 2
probe_mctash posix_compat "--posix" "${PARITY_COMPAT}" 0 0

probe_pair_parity \
  "declare_index_assoc_roundtrip" \
  'declare -a arr; arr[0]=a; arr[1]=b; echo "a1:${arr[1]} s:${arr}"; declare -A map; map[k]=v; echo "mk:${map[k]}"'

if [[ "$STRICT" == "0" ]]; then
  echo "[INFO] STRICT=0: mctash checks are informational while compat gates are under implementation"
fi

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] posix/bash_compat matrix"
  exit 1
fi

echo "[PASS] posix/bash_compat matrix"
