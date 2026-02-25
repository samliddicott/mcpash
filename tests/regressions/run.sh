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

# Reserved-word contextualization checks.
run_case \
  "reserved_words_as_literals" \
  'echo then do in fi' \
  0 \
  $'then do in fi\n'

run_case \
  "reserved_word_for_loop_var_in" \
  'for in in a b; do echo $in; done' \
  0 \
  $'a\nb\n'

run_case \
  "reserved_word_case_pattern_in" \
  'case in in in) echo ok;; esac' \
  0 \
  $'ok\n'

run_case \
  "reserved_word_invalid_context_then" \
  'for i in a b; then echo x; done' \
  2 \
  $'\n' \
  'expected do'

printf '[PASS] reserved-word contextualization regressions\n'

# Startup option parity checks.
set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -eu -c 'echo "$-"' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_short_options: expected status 0, got $status"
grep -Eq '^[[:alpha:]]*e[[:alpha:]]*u[[:alpha:]]*$' "$tmpdir/out" || fail "startup_short_options: expected \$- to include e and u"
printf '[PASS] startup_short_options\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -o nounset -c 'echo "$-"' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_long_option: expected status 0, got $status"
grep -Eq '^[[:alpha:]]*u[[:alpha:]]*$' "$tmpdir/out" || fail "startup_long_option: expected \$- to include u"
printf '[PASS] startup_long_option\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -u -c 'echo $UNSET' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "startup_nounset_status: expected status 2, got $status"
grep -Fq 'unbound variable: UNSET' "$tmpdir/err" || fail "startup_nounset_status: expected unbound variable diagnostic"
printf '[PASS] startup_nounset_status\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -z -c 'echo hi' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "startup_illegal_option: expected status 2, got $status"
grep -Fq 'illegal option -- z' "$tmpdir/err" || fail "startup_illegal_option: expected illegal option diagnostic"
printf '[PASS] startup_illegal_option\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'set -o' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "set_dash_o_list: expected status 0, got $status"
grep -Fq 'Current option settings' "$tmpdir/out" || fail "set_dash_o_list: missing header"
grep -Fq 'errexit' "$tmpdir/out" || fail "set_dash_o_list: missing errexit row"
printf '[PASS] set_dash_o_list\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'set +o' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "set_plus_o_list: expected status 0, got $status"
grep -Fq 'set +o errexit' "$tmpdir/out" || fail "set_plus_o_list: missing errexit line"
grep -Fq 'set +o nolog' "$tmpdir/out" || fail "set_plus_o_list: missing nolog line"
grep -Fq 'set +o debug' "$tmpdir/out" || fail "set_plus_o_list: missing debug line"
printf '[PASS] set_plus_o_list\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'set -o nolog; set -o debug; set -o' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "set_o_nolog_debug: expected status 0, got $status"
grep -Eq '^nolog[[:space:]]+on$' "$tmpdir/out" || fail "set_o_nolog_debug: expected nolog on"
grep -Eq '^debug[[:space:]]+on$' "$tmpdir/out" || fail "set_o_nolog_debug: expected debug on"
printf '[PASS] set_o_nolog_debug\n'

workdir="$tmpdir/globtest"
mkdir -p "$workdir"
touch "$workdir/a" "$workdir/b"

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -f -c "cd '$workdir'; echo *" >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_noglob_behavior: expected status 0, got $status"
grep -Fxq '*' "$tmpdir/out" || fail "startup_noglob_behavior: expected literal '*' output"
printf '[PASS] startup_noglob_behavior\n'

noclobber_file="$tmpdir/noclobber.txt"
printf 'one\n' >"$noclobber_file"
set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -C -c "echo two > '$noclobber_file'; cat '$noclobber_file'" >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_noclobber_behavior: expected shell status 0, got $status"
grep -Fxq 'one' "$tmpdir/out" || fail "startup_noclobber_behavior: expected file content to remain 'one'"
grep -Fq 'file exists' "$tmpdir/err" || fail "startup_noclobber_behavior: expected noclobber diagnostic"
printf '[PASS] startup_noclobber_behavior\n'

printf '[PASS] all regressions (including startup options)\n'
