#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): return/exit status propagation.

set +e
f_ret() {
  return 7
}
f_ret
printf 'ret-func:%s\n' "$?"

( exit 9 )
printf 'exit-subshell:%s\n' "$?"
