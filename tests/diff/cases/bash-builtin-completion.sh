#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: complete/compgen/compopt/bind non-interactive core statuses.
set +e

compgen -b >/dev/null 2>&1
s1=$?
compgen -A builtin ec >/dev/null 2>&1
s2=$?
compgen -A builtin zzzz >/dev/null 2>&1
s3=$?

complete -W 'one two' mycmd >/dev/null 2>&1
s4=$?
complete -p mycmd >/dev/null 2>&1
s5=$?
compopt -o nospace mycmd >/dev/null 2>&1
s6=$?
complete -r mycmd >/dev/null 2>&1
s7=$?
complete -p mycmd >/dev/null 2>&1
s8=$?

bind -q self-insert >/dev/null 2>&1
s9=$?
bind -q __nope__ >/dev/null 2>&1
s10=$?
bind -r '\C-a' >/dev/null 2>&1
s11=$?

printf 'cmp:%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' "$s1" "$s2" "$s3" "$s4" "$s5" "$s6" "$s7" "$s8" "$s9" "$s10" "$s11"
