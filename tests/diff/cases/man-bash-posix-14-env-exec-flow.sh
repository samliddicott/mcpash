#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix category 5): env propagation and exec flow boundaries.

set +e

X0=base
X1=one env | grep '^X1=' | sed -n '1p' | awk -F= '{print "env-prefix:"$2}'
printf 'x0:%s\n' "$X0"

X2=two sh -c 'printf "subenv:%s\\n" "$X2"'
printf 'x2-parent:%s\n' "${X2-}"

( export Z=9; sh -c 'echo in-subshell:$Z' ) | sed -n '1p'
echo "after-subshell:${Z-}"

# Ensure command-not-found in pipeline still leaves shell alive.
( no_such_cmd_abc | cat >/dev/null ) >/dev/null 2>&1
printf 'pipeline-miss:%s\n' "$?"

echo done
