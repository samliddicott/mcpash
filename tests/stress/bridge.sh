#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPEATS="${BRIDGE_STRESS_REPEATS:-100}"
FAIL_FAST="${BRIDGE_STRESS_FAIL_FAST:-1}"
MODE="${BRIDGE_STRESS_UNSHARE_MODE:-auto}"

run_case() {
  local name="$1"
  local script="$2"
  local expect_status="$3"
  local expect_stdout="$4"
  local expect_stderr_substr="${5:-}"
  local iter="$6"

  local out err status got
  out="$(mktemp)"
  err="$(mktemp)"
  set +e
  PYTHONPATH="$ROOT/src" MCTASH_TEST_MODE=1 MCTASH_MODE=posix MCTASH_UNSHARE_MODE="$MODE" python3 -m mctash -c "$script" >"$out" 2>"$err"
  status=$?
  set -e

  if [[ "$status" -ne "$expect_status" ]]; then
    echo "[FAIL] ${name} iter=${iter}: expected status ${expect_status}, got ${status}" >&2
    sed 's/^/  /' "$out" >&2 || true
    sed 's/^/  /' "$err" >&2 || true
    rm -f "$out" "$err"
    return 1
  fi

  got="$(cat "$out")"
  if [[ "$got"$'\n' != "$expect_stdout" ]]; then
    echo "[FAIL] ${name} iter=${iter}: stdout mismatch" >&2
    echo "  expected: $(printf %q "$expect_stdout")" >&2
    echo "  got:      $(printf %q "$got"$'\n')" >&2
    sed 's/^/  /' "$err" >&2 || true
    rm -f "$out" "$err"
    return 1
  fi

  if [[ -n "$expect_stderr_substr" ]] && ! grep -Fq "$expect_stderr_substr" "$err"; then
    echo "[FAIL] ${name} iter=${iter}: stderr missing '$expect_stderr_substr'" >&2
    sed 's/^/  /' "$err" >&2 || true
    rm -f "$out" "$err"
    return 1
  fi

  rm -f "$out" "$err"
  return 0
}

checks=0
fails=0

for ((i=1; i<=REPEATS; i++)); do
  checks=$((checks + 1))
  if ! run_case \
    "python_colon_dispatch_stability" \
    'python: import math; python: -r out math.sqrt 81; echo "$out"' \
    0 \
    $'9.0\n' \
    "" \
    "$i"; then
    fails=$((fails + 1))
    [[ "$FAIL_FAST" == "1" ]] && exit 1
  fi

  checks=$((checks + 1))
  if ! run_case \
    "structured_exception_reset_stability" \
    'py -x "raise ValueError(\"boom\")"; py -x "pass"; echo "X${PYTHON_EXCEPTION}Y|X${PYTHON_EXCEPTION_MSG}Y|X${PYTHON_EXCEPTION_LANG}Y"' \
    0 \
    $'XY|XY|XY\n' \
    "" \
    "$i"; then
    fails=$((fails + 1))
    [[ "$FAIL_FAST" == "1" ]] && exit 1
  fi

  checks=$((checks + 1))
  if ! run_case \
    "deferred_type_contract_stability" \
    'py "sh.vars[\"L\"]=[\"a\"]"' \
    1 \
    $'\n' \
    'TypeError: sh.vars list/tuple mapping is deferred in ash mode' \
    "$i"; then
    fails=$((fails + 1))
    [[ "$FAIL_FAST" == "1" ]] && exit 1
  fi

  if (( i % 10 == 0 )) || (( i == REPEATS )); then
    echo "[INFO] bridge-stress mode=${MODE} progress=${i}/${REPEATS}"
  fi
done

pass=$((checks - fails))
echo "[INFO] bridge-stress summary checks=${checks} pass=${pass} fail=${fails}"
if (( fails > 0 )); then
  echo "[FAIL] bridge-stress detected intermittent failures"
  exit 1
fi
echo "[PASS] bridge-stress strict pass (${REPEATS} repeats, mode=${MODE})"
