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
  "assign_plus_equal" \
  'x=a; x+=b; echo $x' \
  0 \
  $'ab\n'

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
  "python_block_structured_exception" \
  $'PYTHON -x\nraise ValueError("zb")\nEND_PYTHON\necho "$PYTHON_EXCEPTION|$PYTHON_EXCEPTION_MSG|$PYTHON_EXCEPTION_LANG"' \
  0 \
  $'ValueError|zb|python\n'

run_case \
  "python_block_missing_terminator" \
  $'PYTHON\nprint("x")' \
  2 \
  $'\n' \
  'missing END_PYTHON'

run_case \
  "python_block_dedent_default" \
  $'PYTHON\n    if True:\n        print("ded")\nEND_PYTHON' \
  0 \
  $'ded\n'

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
  "py_bash_alias_mapping" \
  'py '"'"'bash.vars["BRIDGE_B"]="ok"'"'"'; echo "$BRIDGE_B"' \
  0 \
  $'ok\n'

run_case \
  "py_sh_fn_callable_from_shell" \
  'py '"'"'sh.fn["pyadd"]=lambda a,b:int(a)+int(b)'"'"'; pyadd 2 3' \
  0 \
  $'5\n'

run_case \
  "py_sh_call_basic" \
  "py -e 'sh(\"echo hi\")'" \
  0 \
  $'hi\n'

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
  "py_sh_popen_capture" \
  'py '"'"'p=sh.popen("echo pop", stdout=sh.PIPE); out,_=p.communicate(); sh.vars["PO"]=out.strip()'"'"'; echo "$PO"' \
  0 \
  $'pop\n'

run_case \
  "param_len_special_at_star" \
  'set -- aa b; echo ${#@}; echo ${#*}' \
  0 \
  $'4\n4\n'

run_case \
  "getopts_bad_var_name" \
  'getopts ab 1x -a; echo s:$?' \
  0 \
  $'s:2\n' \
  'bad variable name'

run_case \
  "getopts_silent_missing_arg" \
  'OPTIND=1; getopts :a: opt -a; echo "s:$? opt:$opt arg:$OPTARG ind:$OPTIND"' \
  0 \
  $'s:0 opt:: arg:a ind:2\n'

run_case \
  "getopts_missing_arg_nonsilent" \
  'OPTIND=1; getopts a: opt -a; echo "s:$? opt:$opt arg:$OPTARG ind:$OPTIND"' \
  0 \
  $'s:0 opt:? arg: ind:2\n' \
  'No arg for -a option'

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
  'expecting "do"'

run_case \
  "reserved_word_function_name_ksh_style" \
  'then() { echo x; }; then' \
  2 \
  $'\n' \
  'unexpected "then"'

run_case \
  "reserved_word_function_name_function_kw" \
  'function then { echo x; }; then' \
  2 \
  $'\n' \
  'invalid function name'

printf '[PASS] reserved-word contextualization regressions\n'

# Parser rejection checks for ambiguous/unterminated constructs.
run_case \
  "parser_unterminated_double_quote" \
  'echo "unterminated' \
  2 \
  $'\n' \
  'unterminated quoted string'

run_case \
  "parser_missing_done" \
  'while true; do echo x' \
  2 \
  $'\n' \
  'unexpected end of file'

run_case \
  "parser_unexpected_close_paren" \
  ')' \
  2 \
  $'\n' \
  'unexpected'

printf '[PASS] parser rejection regressions\n'

# Diagnostic formatting checks.
set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'function then { echo x; }; then' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "diag_function_name: expected status 2, got $status"
grep -Eq '^mctash -c: line 1: syntax error:' "$tmpdir/err" || fail "diag_function_name: expected line-prefixed syntax error"
printf '[PASS] diag_function_name\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'for i in a b; then echo x; done' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "diag_expected_do: expected status 2, got $status"
grep -Eq '^mctash -c: line 1: syntax error:' "$tmpdir/err" || fail "diag_expected_do: expected line-prefixed syntax error"
grep -Fq 'expecting "do"' "$tmpdir/err" || fail "diag_expected_do: expected hint about do"
printf '[PASS] diag_expected_do\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'if true; do echo x; fi' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "diag_expected_then: expected status 2, got $status"
grep -Eq '^mctash -c: line 1: syntax error:' "$tmpdir/err" || fail "diag_expected_then: expected line-prefixed syntax error"
grep -Fq 'unexpected ")"' "$tmpdir/err" || fail "diag_expected_then: expected unexpected \")\" diagnostic"
printf '[PASS] diag_expected_then\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -c 'while true; do echo x' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "diag_expected_done_eof: expected status 2, got $status"
grep -Eq '^mctash -c: line 1: syntax error:' "$tmpdir/err" || fail "diag_expected_done_eof: expected line-prefixed syntax error"
grep -Fq 'expecting "done"' "$tmpdir/err" || fail "diag_expected_done_eof: expected hint about done"
printf '[PASS] diag_expected_done_eof\n'

printf '[PASS] diagnostic format regressions\n'

cat >"$tmpdir/asdl_do_group.sh" <<'EOF'
while false; do
  echo x
done
EOF
set +e
PYTHONPATH="$ROOT/src" python3 -m mctash --dump-lst "$tmpdir/asdl_do_group.sh" >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "asdl_do_group_mapping: expected status 0, got $status"
grep -Fq '"type": "command.DoGroup"' "$tmpdir/out" || fail "asdl_do_group_mapping: expected command.DoGroup in ASDL dump"
printf '[PASS] asdl_do_group_mapping\n'

cat >"$tmpdir/asdl_arith_expr.sh" <<'EOF'
a=1
echo $((a+2*3))
echo $((-a))
echo $((a+=4))
EOF
set +e
PYTHONPATH="$ROOT/src" python3 -m mctash --dump-lst "$tmpdir/asdl_arith_expr.sh" >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "asdl_arith_expr_mapping: expected status 0, got $status"
grep -Fq '"type": "arith_expr.VarSub"' "$tmpdir/out" || fail "asdl_arith_expr_mapping: missing arith_expr.VarSub"
grep -Fq '"type": "arith_expr.Binary"' "$tmpdir/out" || fail "asdl_arith_expr_mapping: missing arith_expr.Binary"
grep -Fq '"type": "arith_expr.Unary"' "$tmpdir/out" || fail "asdl_arith_expr_mapping: missing arith_expr.Unary"
grep -Fq '"type": "arith_expr.BinaryAssign"' "$tmpdir/out" || fail "asdl_arith_expr_mapping: missing arith_expr.BinaryAssign"
printf '[PASS] asdl_arith_expr_mapping\n'

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
