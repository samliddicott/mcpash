#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): alias/unalias/eval/exec/echo/printf/umask/times/ulimit/exit-status

set +e
alias ll='echo ALIAS_LL'
ll
unalias ll
ll >/dev/null 2>&1
printf 'unalias-miss:%s\n' "$?"

eval 'EVAL_VAR=42'
printf 'eval:%s\n' "$EVAL_VAR"

exec 3>&1
printf 'fd3-open\n' >&3
exec 3>&-

echo 'echo:ok'
printf 'printf:%s\n' 'ok'

old_umask=$(umask)
umask 022
printf 'umask:%s\n' "$(umask)"
umask "$old_umask"

times | sed -n '1p'

cur_ul=$(ulimit -n)
printf 'ulimit-n:%s\n' "$cur_ul"

false
printf 'false:%s\n' "$?"
true
printf 'true:%s\n' "$?"
