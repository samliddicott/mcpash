#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SHELL_CMD=(python3 -m mctash)

tmpdir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  if [[ -f "$tmpdir/out" ]]; then
    printf '  stdout:\n' >&2
    sed 's/^/    /' "$tmpdir/out" >&2 || true
  fi
  if [[ -f "$tmpdir/err" ]]; then
    printf '  stderr:\n' >&2
    sed 's/^/    /' "$tmpdir/err" >&2 || true
  fi
  exit 1
}

run_case() {
  local name="$1"
  local script="$2"
  local expect_status="$3"
  local expect_stdout="$4"
  local stderr_substr="${5:-}"

  set +e
  PYTHONPATH="$ROOT/src" MCTASH_TEST_MODE=1 "${SHELL_CMD[@]}" -c "$script" >"$tmpdir/out" 2>"$tmpdir/err"
  local status=$?
  set -e
  if [[ "$status" -ne "$expect_status" ]]; then
    fail "${name}: expected status ${expect_status}, got ${status}"
  fi

  local actual_stdout
  actual_stdout="$(cat "$tmpdir/out")"
  if [[ "$actual_stdout"$'\n' != "$expect_stdout" ]]; then
    fail "${name}: stdout mismatch"
  fi

  if [[ -n "$stderr_substr" ]]; then
    if ! grep -Fq "$stderr_substr" "$tmpdir/err"; then
      fail "${name}: expected stderr to contain '$stderr_substr'"
    fi
  fi

  printf '[PASS] %s\n' "$name"
}

run_case \
  "py_statement_exec" \
  "py 'print(\"ok\")'" \
  0 \
  $'ok\n'

run_case \
  "py_eval_print" \
  "py -e '1+2'" \
  0 \
  $'3\n'

run_case \
  "py_persistent_state" \
  "py 'x=7'; py -e 'x'" \
  0 \
  $'7\n'

run_case \
  "py_stdout_capture_var" \
  'py -v out '"'"'print("cap")'"'"'; echo "X${out}Y"' \
  0 \
  $'Xcap\nY\n'

run_case \
  "py_return_capture_var" \
  'py -r out -e '"'"'10+5'"'"'; echo "X${out}Y"' \
  0 \
  $'X15Y\n'

run_case \
  "py_callable_dispatch" \
  'py '"'"'def add(a,b): return int(a)+int(b)'"'"'; py -r out add 2 3; echo "X${out}Y"' \
  0 \
  $'X5Y\n'

run_case \
  "python_colon_callable_dispatch" \
  'py '"'"'import math'"'"'; python: -r out math.sqrt 9; echo "X${out}Y"' \
  0 \
  $'X3.0Y\n'

run_case \
  "python_colon_non_callable_fallback_exec" \
  'python: import math; python: -r out math.pow 2 4; echo "X${out}Y"' \
  0 \
  $'X16.0Y\n'

run_case \
  "py_structured_exception" \
  'py -x '"'"'raise ValueError("boom")'"'"'; echo "$PYTHON_EXCEPTION|$PYTHON_EXCEPTION_MSG|$PYTHON_EXCEPTION_LANG"; case "$PYTHON_EXCEPTION_TB" in *"<string>"*) echo s:0;; *) echo s:1;; esac' \
  0 \
  $'ValueError|boom|python\ns:0\n'

run_case \
  "py_exception_status" \
  'py '"'"'raise RuntimeError("bad")'"'"'; echo s:$?' \
  0 \
  $'s:1\n' \
  'RuntimeError: bad'

run_case \
  "python_block_basic" \
  $'PYTHON\nprint("blk")\nEND_PYTHON' \
  0 \
  $'blk\n'

run_case \
  "python_block_no_dedent" \
  $'PYTHON --no-dedent\n    print("nd")\nEND_PYTHON\necho s:$?' \
  0 \
  $'s:1\n' \
  'IndentationError'

run_case \
  "py_sh_vars_mapping" \
  'py '"'"'sh.vars["BRIDGE_X"]="42"'"'"'; echo "$BRIDGE_X"' \
  0 \
  $'42\n'

run_case \
  "py_sh_fn_callable_from_shell" \
  'py '"'"'sh.fn["pyadd"]=lambda a,b:int(a)+int(b)'"'"'; pyadd 2 3' \
  0 \
  $'5\n'

run_case \
  "py_sh_run_capture_output" \
  'py '"'"'cp=sh.run("echo rr", capture_output=True); sh.vars["R"]=cp.stdout.strip()'"'"'; echo "$R"' \
  0 \
  $'rr\n'

run_case \
  "py_sh_run_check_error" \
  'py -x '"'"'sh.run("exit 7", check=True)'"'"'; echo "$PYTHON_EXCEPTION"' \
  0 \
  $'ShellCalledProcessError\n'

run_case \
  "py_tie_scalar_roundtrip" \
  'py '"'"'x="seed"'"'"'; py -t x; x=after; py -e '"'"'x'"'"'' \
  0 \
  $'after\n'

run_case \
  "py_tie_readonly_write_error" \
  'py '"'"'sh.tie("RO", lambda: "r", None)'"'"'; RO=x' \
  1 \
  $'\n' \
  'tied variable is read-only'

run_case \
  "from_import_callable_wrapper" \
  'from math import factorial as fac; fac 5' \
  0 \
  $'120\n'

run_case \
  "py_sh_stack_contains_function" \
  "f(){ py -e 'next((fr[\"funcname\"] for fr in sh.stack if fr[\"funcname\"]==\"f\"), \"\")'; }; f" \
  0 \
  $'f\n'

printf '[PASS] bridge conformance suite\n'
