#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): cd/pwd/command/type/hash

set +e
orig=$(pwd)
cd / >/dev/null 2>&1
printf 'pwd-root:%s\n' "$(pwd)"
cd "$orig" >/dev/null 2>&1
printf 'pwd-back:%s\n' "$(pwd)"

command -v echo
command -v no_such_cmd
printf 'command-miss:%s\n' "$?"

type echo
type no_such_cmd
printf 'type-miss:%s\n' "$?"

hash -r
hash printf
hash no_such_cmd
printf 'hash-miss:%s\n' "$?"
