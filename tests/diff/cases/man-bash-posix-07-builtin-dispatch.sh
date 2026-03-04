#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): builtin dispatch behavior.

set +e
builtin echo builtin-ok

builtin no_such_builtin >/dev/null 2>&1
printf 'builtin-miss:%s\n' "$?"

# Shadow echo with a function; builtin should bypass function.
echo() { printf 'fn-echo\n'; }
echo
builtin echo real-echo
