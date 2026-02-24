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
  PYTHONPATH="$ROOT/src" "${SHELL_CMD[@]}" -c "$script" >"$tmpdir/out" 2>"$tmpdir/err"
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
  "read_ifs_double_separator" \
  'echo "::" | ( IFS=": " read x y; echo "($x)($y)" )' \
  0 \
  $'()()\n'

run_case \
  "read_ifs_triple_separator" \
  'echo ":::" | ( IFS=": " read x y; echo "($x)($y)" )' \
  0 \
  $'()(::)\n'

run_case \
  "pipefail_toggle" \
  'false | true; echo d:$?; set -o pipefail; false | true; echo p:$?' \
  0 \
  $'d:0\np:1\n'

run_case \
  "pipeline_control_flow_status" \
  'exit 2 | exit 3 | exit 4; echo s:$?' \
  0 \
  $'s:4\n'

run_case \
  "redir_bad_fd_builtin" \
  'echo hi >&100; echo s:$?' \
  0 \
  $'s:1\n' \
  'Bad file descriptor'

run_case \
  "slash_path_permission_denied" \
  './; echo s:$?' \
  0 \
  $'s:126\n' \
  'Permission denied'

run_case \
  "slash_path_not_found" \
  './this-definitely-does-not-exist; echo s:$?' \
  0 \
  $'s:127\n' \
  'not found'

printf '[PASS] all targeted regressions\n'
