#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): cd/pwd/command/type/hash

set +e
orig=$(pwd)
cd / >/dev/null 2>&1
printf 'pwd-root:%s\n' "$(pwd)"
cd "$orig" >/dev/null 2>&1
printf 'pwd-back:%s\n' "$(pwd)"

command -v echo | sed -n '1p' | awk '{print "command-v-echo:"$0}'
command -v no_such_cmd >/dev/null 2>&1
printf 'command-miss:%s\n' "$?"

type echo >/dev/null 2>&1
printf 'type-hit:%s\n' "$?"
type no_such_cmd >/dev/null 2>&1
printf 'type-miss:%s\n' "$?"

hash -r
hash printf
hash no_such_cmd >/dev/null 2>&1
printf 'hash-miss:%s\n' "$?"
