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
  local extra_env="${6:-}"

  set +e
  if [[ -n "$extra_env" ]]; then
    read -r -a _extra_env_parts <<<"$extra_env"
    env "${_extra_env_parts[@]}" PYTHONPATH="$ROOT/src" MCTASH_TEST_MODE=1 "${SHELL_CMD[@]}" -c "$script" >"$tmpdir/out" 2>"$tmpdir/err"
  else
    PYTHONPATH="$ROOT/src" MCTASH_TEST_MODE=1 "${SHELL_CMD[@]}" -c "$script" >"$tmpdir/out" 2>"$tmpdir/err"
  fi
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
  "fc_list_last_two" \
  "py 'sh._rt._history=[\"echo one\",\"echo two\",\"echo three\"]'; fc -l -n 1 2" \
  0 \
  $'echo one\necho two\n'

run_case \
  "fc_list_reverse" \
  "py 'sh._rt._history=[\"echo one\",\"echo two\",\"echo three\"]'; fc -l -r -n 1 2" \
  0 \
  $'echo two\necho one\n'

run_case \
  "fc_substitute_and_reexec" \
  "py 'sh._rt._history=[\"echo alpha\",\"echo beta\"]'; fc -s beta=replay 2" \
  0 \
  $'replay\necho replay\n'

run_case \
  "fc_editor_flag_acceptance" \
  "py 'sh._rt._history=[\"echo one\",\"echo two\"]'; set +e; fc -e : -l -n 1 >/dev/null; echo s:\$?" \
  0 \
  $'s:0\n'

run_case \
  "fc_invalid_reference_status" \
  "py 'sh._rt._history=[\"echo one\"]'; set +e; fc -s 999999 >/dev/null 2>&1; echo s:\$?" \
  0 \
  $'s:1\n'

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
  "py_callable_coercion_diag_on_total_typeerror" \
  'py '"'"'def one(a): return a'"'"'; py one 1 2' \
  1 \
  $'\n' \
  'call failed after automatic coercion and raw-string fallback'

run_case \
  "python_colon_non_callable_fallback_exec_error_diag" \
  'python: math.sqrt 9' \
  1 \
  $'\n' \
  'math.sqrt: not callable, and python-statement fallback failed (SyntaxError: invalid syntax'

run_case \
  "py_structured_exception_reset_on_success" \
  'py -x '"'"'raise ValueError("boom")'"'"'; py -x '"'"'pass'"'"'; echo "X${PYTHON_EXCEPTION}Y|X${PYTHON_EXCEPTION_MSG}Y|X${PYTHON_EXCEPTION_LANG}Y|X${PYTHON_EXCEPTION_TB}Y"' \
  0 \
  $'XY|XY|XY|XY\n'

run_case \
  "py_structured_exception" \
  'py -x '"'"'raise ValueError("boom")'"'"'; echo "$PYTHON_EXCEPTION|$PYTHON_EXCEPTION_MSG|$PYTHON_EXCEPTION_LANG"; case "$PYTHON_EXCEPTION_TB" in *"<string>"*) echo s:0;; *) echo s:1;; esac' \
  0 \
  $'ValueError|boom|python\ns:0\n'

run_case \
  "py_structured_exception_tb_shape" \
  'py -x '"'"'raise RuntimeError("x")'"'"'; case "$PYTHON_EXCEPTION_TB" in *"<string>:1:<module>"*) echo s:0;; *) echo s:1;; esac' \
  0 \
  $'s:0\n'

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
  "python_block_parser_robust_parens_quotes" \
  $'PYTHON\ntext = ")"\nprint("q:\\""+text)\nEND_PYTHON' \
  0 \
  $'q:")\n'

run_case \
  "python_block_in_command_substitution" \
  $'out=$({ PYTHON\nprint("sub")\nEND_PYTHON\n}); echo "$out"' \
  0 \
  $'sub\n'

run_case \
  "python_block_pipeline" \
  $'echo xx | { PYTHON\nimport sys\nprint(sys.stdin.read().strip()+"yy")\nEND_PYTHON\n} | cat' \
  0 \
  $'xxyy\n'

run_case \
  "python_block_inline_end_pipeline" \
  $'PYTHON\nprint("ii")\nEND_PYTHON | cat' \
  0 \
  $'ii\n'

run_case \
  "py_interrupt_status_130" \
  'py '"'"'raise KeyboardInterrupt()'"'"'; echo s:$?' \
  130 \
  $'s:130\n'

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
  "py_sh_vars_attrs" \
  'py '"'"'sh.vars["AX"]="ab"; sh.vars.set_attrs("AX", uppercase=True); sh.vars["AX"]="xy"; print(sh.vars.attrs("AX").get("uppercase", False)); print(sh.vars["AX"])'"'"'' \
  0 \
  $'True\nXY\n'

run_case \
  "py_sh_vars_declare_integer" \
  'py '"'"'sh.vars.declare("IV", "07", integer=True); print(sh.vars["IV"])'"'"'' \
  0 \
  $'7\n'

run_case \
  "py_sh_env_exported" \
  'py '"'"'sh.env["EX_BRIDGE"]="vv"'"'"'; python3 -c '"'"'import os; print(os.getenv("EX_BRIDGE",""))'"'"'' \
  0 \
  $'vv\n'

run_case \
  "py_sh_fn_assignment_declare_wrapper" \
  'py '"'"'sh.fn["sum2"]=lambda a,b:int(a)+int(b)'"'"'; declare -F sum2; sum2 4 6' \
  0 \
  $'sum2\n10\n'

run_case \
  "py_from_import_callable_wrapper" \
  'from math import factorial as fac; declare -F fac; fac 5' \
  0 \
  $'fac\n120\n'

run_case \
  "py_tie_scalar_roundtrip" \
  'py '"'"'x="seed"'"'"'; py -t x; x=after; py -e '"'"'x'"'"'' \
  0 \
  $'after\n'

run_case \
  "py_tie_integer_cast" \
  'py '"'"'n=0; sh.tie("TN", lambda: n, lambda v: globals().__setitem__("n", v), type="integer")'"'"'; TN=12; py -e '"'"'n'"'"'' \
  0 \
  $'12\n'

run_case \
  "py_tie_readonly_write_error" \
  'py '"'"'sh.tie("RO", lambda: "r", None)'"'"'; RO=x' \
  1 \
  $'\n' \
  'tied variable is read-only'

run_case \
  "py_sh_stack_contains_function" \
  "f(){ py -e 'next((fr[\"funcname\"] for fr in sh.stack if fr[\"funcname\"]==\"f\"), \"\")'; }; f" \
  0 \
  $'f\n'

run_case \
  "py_sh_stack_innermost_is_python" \
  "f(){ py -e 'sh.stack[0][\"kind\"]+\":\"+sh.stack[0][\"funcname\"]'; }; f" \
  0 \
  $'python:py\n'

run_case \
  "py_sh_stack_contains_command_subst_frame" \
  'x=$(py -e '"'"'next((fr["kind"] for fr in sh.stack if fr["kind"]=="command_subst"), "")'"'"'); echo "$x"' \
  0 \
  $'command_subst\n'

run_case \
  "shared_builtin_basic" \
  'f="/tmp/mctash-shared-$$.json"; MCTASH_SHARED_FILE="$f" shared SX=12; MCTASH_SHARED_FILE="$f" shared SX; rm -f "$f"' \
  0 \
  $'12\n'

run_case \
  "shared_cross_process_visibility" \
  'f="/tmp/mctash-shared-$$.json"; MCTASH_SHARED_FILE="$f" shared SP=ok; MCTASH_SHARED_FILE="$f" python3 -m mctash -c '"'"'shared SP'"'"'; rm -f "$f"' \
  0 \
  $'ok\n'

run_case \
  "py_sh_vars_list_rejected_in_ash_mode" \
  'py '"'"'sh.vars["LST"]=["a","b"]'"'"'' \
  1 \
  $'\n' \
  'TypeError: sh.vars list/tuple mapping is deferred in ash mode'

run_case \
  "py_sh_vars_dict_rejected_in_ash_mode" \
  'py '"'"'sh.vars["MAP"]={"k":"v"}'"'"'' \
  1 \
  $'\n' \
  'TypeError: sh.vars dict mapping is deferred in ash mode'

run_case \
  "py_tie_array_rejected_in_ash_mode" \
  'py -x '"'"'sh.tie("TA", lambda: ["x"], type="array")'"'"'; echo "$PYTHON_EXCEPTION|$PYTHON_EXCEPTION_MSG"' \
  0 \
  $'ValueError|array tie type is deferred in ash mode\n'

run_case \
  "py_tie_assoc_rejected_in_ash_mode" \
  'py -x '"'"'sh.tie("TM", lambda: {"k":"v"}, type="assoc")'"'"'; echo "$PYTHON_EXCEPTION|$PYTHON_EXCEPTION_MSG"' \
  0 \
  $'ValueError|assoc tie type is deferred in ash mode\n'

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

run_case \
  "hash_builtin_resolve_list" \
  'hash -r; hash ls >/dev/null; case "$(hash)" in *"ls="*) echo ok;; *) echo no;; esac' \
  0 \
  $'ok\n'

run_case \
  "times_builtin_basic" \
  'x=$(times); case "$x" in "") echo no;; *) echo ok;; esac' \
  0 \
  $'ok\n'

run_case \
  "umask_builtin_roundtrip" \
  'old=$(umask); umask 022; echo now:$(umask); umask "$old"' \
  0 \
  $'now:0022\n'

run_case \
  "ulimit_builtin_nofile_get" \
  'ulimit -n >/dev/null; echo s:$?' \
  0 \
  $'s:0\n'

run_case \
  "jobs_builtin_lists_bg" \
  'sleep 0.5 & case "$(jobs)" in "") echo ok;; *) echo no;; esac; wait %1 >/dev/null' \
  0 \
  $'ok\n'

run_case \
  "fg_builtin_waits_job" \
  'sleep 0.2 & fg %1 >/dev/null 2>&1; echo s:$?; wait %1 >/dev/null' \
  0 \
  $'s:2\n'

run_case \
  "bg_builtin_current_job" \
  'sleep 0.2 & bg %1 >/dev/null 2>&1; echo s:$?; wait %1 >/dev/null' \
  0 \
  $'s:2\n'

run_case \
  "declare_array_requires_bash_compat" \
  'declare -a arr; echo s:$?' \
  0 \
  $'s:2\n' \
  'declare -a requires BASH_COMPAT to be set'

run_case \
  "declare_array_enabled_with_bash_compat" \
  'declare -a arr; echo s:$?' \
  0 \
  $'s:0\n' \
  '' \
  'BASH_COMPAT=50'

run_case \
  "declare_assoc_requires_bash_compat" \
  'declare -A map; echo s:$?' \
  0 \
  $'s:2\n' \
  'declare -A requires BASH_COMPAT to be set'

run_case \
  "declare_assoc_enabled_with_bash_compat" \
  'declare -A map; echo s:$?' \
  0 \
  $'s:0\n' \
  '' \
  'BASH_COMPAT=50'

run_case \
  "thread_unshare_fallback_diag" \
  'export MCTASH_UNSHARE_MODE=off MCTASH_THREAD_DIAG=1; ( : ) & wait %1; echo s:$?' \
  0 \
  $'s:0\n' \
  'thread-runtime: unshare disabled'

run_case \
  "process_subst_input_basic" \
  'out=$(cat <(printf "ps-in")); echo "$out"' \
  0 \
  $'ps-in\n'

run_case \
  "process_subst_output_basic" \
  'f="/tmp/mctash-psubst-$$.txt"; printf "hello-ps\n" | cat > >(cat > "$f"); cat "$f"; rm -f "$f"' \
  0 \
  $'hello-ps\n'

run_case \
  "process_subst_cwd_isolation" \
  'orig="$PWD"; printf "x\n" | cat > >(cd /; cat >/dev/null); if [ "$PWD" = "$orig" ]; then echo same; else echo diff; fi' \
  0 \
  $'same\n'

run_case \
  "process_subst_fd_isolation" \
  'pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); printf "y\n" | cat > >(exec 9>/dev/null; cat >/dev/null); post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); echo "$pre:$post"' \
  0 \
  $'no:no\n'

run_case \
  "thread_combined_bg_pipeline_process_subst" \
  'orig="$PWD"; out="/tmp/mctash-combo-out-$$.txt"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); ( cd /; exec 9>/dev/null; printf "combo\n" | cat > >(cat > "$out") ) & wait %1; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; data="$(cat "$out")"; rm -f "$out"; [ "$after" = "$orig" ] && c=same || c=diff; echo "$pre:$post:$c:$data"' \
  0 \
  $'no:no:same:combo\n'

run_case \
  "thread_multi_job_concurrency_isolation" \
  'orig="$PWD"; p1="/tmp/mctash-conc-a-$$.txt"; p2="/tmp/mctash-conc-b-$$.txt"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); ( cd /; exec 9>/dev/null; printf "A\n" | cat > >(cat > "$p1") ) & j1=$!; ( cd /tmp; exec 9>/dev/null; printf "B\n" | cat > >(cat > "$p2") ) & j2=$!; wait "$j1"; wait "$j2"; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; [ "$after" = "$orig" ] && c=same || c=diff; data=$(cat "$p1" "$p2" | sort | tr -d "\n"); rm -f "$p1" "$p2"; echo "$pre:$post:$c:$data"' \
  0 \
  $'no:no:same:AB\n'

run_case \
  "thread_unshare_forced_fail_diag" \
  'export MCTASH_UNSHARE_MODE=fail MCTASH_THREAD_DIAG=1; ( : ) & wait %1; echo s:$?' \
  0 \
  $'s:0\n' \
  'thread-runtime: unshare forced-fail'

run_case \
  "thread_high_load_concurrency_isolation" \
  'orig="$PWD"; d="/tmp/mctash-stress-$$"; mkdir -p "$d"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); pids=""; for i in 1 2 3 4 5; do ( cd /; exec 9>/dev/null; printf "J$i\n" | cat > >(cat > "$d/$i.out") ) & pids="$pids $!"; done; for p in $pids; do wait "$p"; done; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; [ "$after" = "$orig" ] && c=same || c=diff; count=$(cat "$d"/*.out | wc -l | tr -d " "); miss=0; for i in 1 2 3 4 5; do grep -qx "J$i" "$d/$i.out" || miss=$((miss+1)); done; rm -rf "$d"; echo "$pre:$post:$c:$count:$miss"' \
  0 \
  $'no:no:same:5:0\n'

run_case \
  "monitor_mode_noninteractive_diag" \
  'set -m >/dev/null; echo s:$?' \
  0 \
  $'s:0\n' \
  "can't access tty; job control turned off"

run_case \
  "thread_long_running_mixed_stress" \
  'orig="$PWD"; base="/tmp/mctash-stress2-$$"; rm -rf "$base"; mkdir -p "$base"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); miss=0; total=0; for r in 1 2 3 4 5 6; do d="$base/$r"; mkdir -p "$d"; pids=""; for i in 1 2 3; do ( cd /; exec 9>/dev/null; printf "R${r}J${i}\n" | cat > >(cat > "$d/$i.out") ) & pids="$pids $!"; done; for p in $pids; do wait "$p"; done; for i in 1 2 3; do total=$((total+1)); grep -qx "R${r}J${i}" "$d/$i.out" || miss=$((miss+1)); done; done; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; [ "$after" = "$orig" ] && c=same || c=diff; rm -rf "$base"; echo "$pre:$post:$c:$miss:$total"' \
  0 \
  $'no:no:same:0:18\n'

run_case \
  "monitor_mode_interactive_pty" \
  'out=$(PYTHONPATH=src script -qec "python3 -m mctash -i -c '\''set -m; sleep 0.05 & jobs -p >/dev/null; echo m:\$?; wait'\''" /dev/null | tr -d "\r"); echo "$out"' \
  0 \
  $'m:0\n'

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

# ASDL executor-path checks (command dispatch runs directly on ASDL nodes).
run_case \
  "asdl_exec_brace_group" \
  '{ x=ok; echo "$x"; }' \
  0 \
  $'ok\n'

run_case \
  "asdl_exec_if_arms" \
  'if false; then echo a; elif true; then echo b; else echo c; fi' \
  0 \
  $'b\n'

run_case \
  "asdl_exec_while_until" \
  'i=0; while [ "$i" -lt 2 ]; do i=$((i+1)); done; echo w:$i; until [ "$i" -eq 4 ]; do i=$((i+1)); done; echo u:$i' \
  0 \
  $'w:2\nu:4\n'

run_case \
  "asdl_exec_controlflow_break_arg" \
  'for i in 1 2 3; do break 1; echo never; done; echo ok' \
  0 \
  $'ok\n'

run_case \
  "asdl_exec_controlflow_return_arg" \
  'f(){ return 7; }; f; echo s:$?' \
  0 \
  $'s:7\n'

run_case \
  "asdl_exec_for_native_word_expansion" \
  'x="a b"; for i in "$x" c; do echo "<$i>"; done' \
  0 \
  $'<a b>\n<c>\n'

run_case \
  "asdl_exec_case_native_word_expansion" \
  'v=fooz; p="foo*"; case "$v" in $p) echo m;; *) echo n;; esac' \
  0 \
  $'m\n'

run_case \
  "asdl_exec_case_quoted_pattern_literal_semantics" \
  'v=fooz; p="foo*"; case "$v" in "$p") echo m;; *) echo n;; esac' \
  0 \
  $'n\n'

run_case \
  "asdl_exec_shassignment_word_semantics" \
  'x="a b"; y=$x; echo "<$y>"' \
  0 \
  $'<a b>\n'

run_case \
  "asdl_exec_shassignment_escaped_quote_semantics" \
  "x=\\'B; echo \"\${x#\\'}\"" \
  0 \
  $'B\n'

run_case \
  "asdl_exec_shassignment_arith_word_semantics" \
  'x=$((1+2*3)); echo "<$x>"' \
  0 \
  $'<7>\n'

run_case \
  "asdl_exec_shassignment_var_concat_semantics" \
  'a=foo; x=${a}bar; echo "<$x>"' \
  0 \
  $'<foobar>\n'

run_case \
  "asdl_exec_shassignment_braced_default_semantics" \
  'unset a; x=${a:-fallback}; echo "<$x>"' \
  0 \
  $'<fallback>\n'

run_case \
  "asdl_exec_shassignment_braced_alt_semantics" \
  'a=1; x=${a:+alt}; echo "<$x>"' \
  0 \
  $'<alt>\n'

run_case \
  "asdl_exec_shassignment_braced_len_semantics" \
  'a=abcd; x=${#a}; echo "<$x>"' \
  0 \
  $'<4>\n'

run_case \
  "asdl_exec_shassignment_cmdsub_status" \
  'x=$(exit 7); echo s:$?' \
  0 \
  $'s:7\n'

run_case \
  "asdl_exec_shassignment_cmdsub_text_semantics" \
  'x=$(printf hi); y=${x}x; echo "<$y>"' \
  0 \
  $'<hix>\n'

printf '[PASS] asdl executor-path regressions\n'

# Quoted argv behavior guardrails for upcoming ASDL argv-native work.
run_case \
  "asdl_argv_dquote_prevent_param_expansion" \
  'x=7; echo "m:\$x"' \
  0 \
  $'m:$x\n'

run_case \
  "asdl_argv_dquote_allow_param_expansion" \
  'x=7; echo "m:$x"' \
  0 \
  $'m:7\n'

run_case \
  "asdl_argv_dquote_escape_quote_char" \
  'echo "a\"b"' \
  0 \
  $'a"b\n'

run_case \
  "asdl_argv_dquote_keep_backslash_nonmeta" \
  'echo "a\qb"' \
  0 \
  $'a\qb\n'

run_case \
  "asdl_argv_mixed_quote_backslash_semantics" \
  'echo a"\\"b' \
  0 \
  $'a\\b\n'

run_case \
  "asdl_argv_dquote_var_preserve_spaces" \
  'x="a b"; set -- "m:$x"; echo "$#|$1"' \
  0 \
  $'1|m:a b\n'

run_case \
  "asdl_argv_dquote_braced_default_preserve_spaces" \
  'unset x; set -- "x=${x:-a b}"; echo "$#|$1"' \
  0 \
  $'1|x=a b\n'

run_case \
  "asdl_argv_simple_var_split_semantics" \
  'x="a b"; set -- $x; echo "$#|$1|$2"' \
  0 \
  $'2|a|b\n'

run_case \
  "asdl_argv_simple_var_scalar_semantics" \
  'x=abc; echo "<$x>"' \
  0 \
  $'<abc>\n'

run_case \
  "asdl_argv_braced_var_scalar_semantics" \
  'x=abc; echo "<${x}>"' \
  0 \
  $'<abc>\n'

run_case \
  "asdl_argv_braced_default_single_quoted_semantics" \
  'unset x; set -- ${x-'"'"'a b'"'"'}; echo "$#|$1|$2"' \
  0 \
  $'1|a b|\n'

printf '[PASS] quoted argv guardrails\n'

# Malformed parameter-expansion guardrails:
# preserve error behavior (status/flow), not exact diagnostic wording.
run_case \
  "bad_subst_plus_form_errors" \
  'echo ${+}; echo never' \
  2 \
  $'\n' \
  'bad substitution'

run_case \
  "bad_subst_colon_form_errors" \
  'echo ${:1}; echo never' \
  2 \
  $'\n' \
  'bad substitution'

run_case \
  "bad_subst_amp_form_errors" \
  'echo ${&}; echo never' \
  2 \
  $'\n' \
  'bad substitution'

run_case \
  "bad_subst_for_in_errors" \
  'for i in ${+}; do echo x; done; echo never' \
  2 \
  $'\n' \
  'bad substitution'

run_case \
  "bad_subst_case_pattern_errors" \
  'x=a; case "$x" in ${+}) echo x;; esac; echo never' \
  2 \
  $'\n' \
  'bad substitution'

run_case \
  "bad_subst_redir_target_errors" \
  'echo hi > ${+}; echo never' \
  2 \
  $'\n' \
  'bad substitution'

printf '[PASS] bad-substitution guardrails\n'

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
PYTHONPATH="$ROOT/src" python3 -m mctash --posix -c 'set -o | sed -n "s/^posix[[:space:]]*//p"' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_posix_long_option: expected status 0, got $status"
grep -Fxq 'on' "$tmpdir/out" || fail "startup_posix_long_option: expected posix to be on"
printf '[PASS] startup_posix_long_option\n'

set +e
PYTHONPATH="$ROOT/src" BASH_COMPAT=50 python3 -m mctash --posix -c 'set -o | sed -n "s/^posix[[:space:]]*//p"; echo "${BASH_COMPAT}"' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_posix_bash_compat_env: expected status 0, got $status"
grep -Fxq 'on' "$tmpdir/out" || fail "startup_posix_bash_compat_env: expected posix to be on"
grep -Fxq '50' "$tmpdir/out" || fail "startup_posix_bash_compat_env: expected BASH_COMPAT env to be visible"
printf '[PASS] startup_posix_bash_compat_env\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -u -c 'echo $UNSET' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 2 ]] || fail "startup_nounset_status: expected status 2, got $status"
grep -Fq 'unbound variable: UNSET' "$tmpdir/err" || fail "startup_nounset_status: expected unbound variable diagnostic"
printf '[PASS] startup_nounset_status\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -v -c 'echo hi' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_verbose_option: expected status 0, got $status"
grep -Fxq 'hi' "$tmpdir/out" || fail "startup_verbose_option: expected stdout hi"
grep -Fq 'echo hi' "$tmpdir/err" || fail "startup_verbose_option: expected echoed input on stderr"
printf '[PASS] startup_verbose_option\n'

set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -x -c 'PS4="TRACE> "; echo hi' >"$tmpdir/out" 2>"$tmpdir/err"
status=$?
set -e
[[ "$status" -eq 0 ]] || fail "startup_xtrace_ps4: expected status 0, got $status"
grep -Fxq 'hi' "$tmpdir/out" || fail "startup_xtrace_ps4: expected stdout hi"
grep -Fq 'TRACE> echo hi' "$tmpdir/err" || fail "startup_xtrace_ps4: expected PS4 prefix in trace output"
printf '[PASS] startup_xtrace_ps4\n'

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

if ! PYROOT="$ROOT" python3 - <<'PY'
import os
import pty
import select
import subprocess
import time

root = os.environ["PYROOT"]
env = dict(os.environ)
env["PYTHONPATH"] = os.path.join(root, "src")
master, slave = pty.openpty()
p = subprocess.Popen(
    ["python3", "-m", "mctash", "-i"],
    cwd=root,
    stdin=slave,
    stdout=slave,
    stderr=slave,
    env=env,
    close_fds=True,
)
os.close(slave)

def drain(buf: bytearray, rounds: int = 4):
    for _ in range(rounds):
        time.sleep(0.08)
        while True:
            r, _, _ = select.select([master], [], [], 0)
            if not r:
                break
            try:
                buf.extend(os.read(master, 4096))
            except OSError:
                return

out = bytearray()
drain(out)
for line in [b"echo one\n", b"echo two\n", b"fc -l -n -2 -1\n", b"fc -s two=TWO -3\n", b"exit\n"]:
    os.write(master, line)
    drain(out)

p.wait(timeout=5)
text = out.decode("utf-8", "ignore")
ok = ("echo one" in text and "echo two" in text and "echo TWO" in text and "TWO" in text)
if not ok:
    print(text)
    raise SystemExit(1)
PY
then
  fail "interactive_fc_smoke"
fi
printf '[PASS] interactive_fc_smoke\n'
