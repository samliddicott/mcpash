#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MCTASH=(python3 -m mctash)
STRICT="${STRICT:-0}"

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

  if [[ "$STRICT" == "1" ]]; then
    if ! grep -q '^arr:0$' "$out"; then
      echo "[FAIL] mctash ${label}: expected declare -a success in strict mode" >&2
      fail=1
    fi
    if ! grep -q '^assoc:0$' "$out"; then
      echo "[FAIL] mctash ${label}: expected declare -A success in strict mode" >&2
      fail=1
    fi
  fi
}

# Bash reference matrix
probe_bash plain bash
probe_bash posix bash --posix
probe_bash posix_compat50 env BASH_COMPAT=50 bash --posix

# mctash progress matrix
probe_mctash plain "" ""
probe_mctash posix "--posix" ""
probe_mctash posix_compat50 "--posix" "50"

if [[ "$STRICT" == "0" ]]; then
  echo "[INFO] STRICT=0: mctash checks are informational while compat gates are under implementation"
fi

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] posix/bash_compat matrix"
  exit 1
fi

echo "[PASS] posix/bash_compat matrix"
