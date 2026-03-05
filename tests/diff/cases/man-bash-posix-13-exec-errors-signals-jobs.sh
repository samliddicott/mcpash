#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix category 5): command lookup/exec status, trap delivery, wait behavior.

set +e

no_such_cmd_xyz >/dev/null 2>&1
printf 'exec-miss:%s\n' "$?"

tmpx="/tmp/mctash-exec-noexec-$$"
printf '#!/bin/sh\necho hi\n' >"$tmpx"
chmod 644 "$tmpx"
"$tmpx" >/dev/null 2>&1
printf 'exec-noexec:%s\n' "$?"
rm -f "$tmpx"

trap 'echo trap:EXIT:$?' EXIT
( exit 7 ) >/dev/null 2>&1
printf 'subshell-exit:%s\n' "$?"
trap - EXIT

trap 'echo trap:USR1' USR1
kill -USR1 $$ >/dev/null 2>&1
sleep 0.05
trap - USR1

sleep 0.1 &
p1=$!
sleep 0.15 &
p2=$!
wait "$p1"
printf 'wait-p1:%s\n' "$?"
wait "$p2"
printf 'wait-p2:%s\n' "$?"

wait 999999 >/dev/null 2>&1
printf 'wait-miss:%s\n' "$?"

jobs -p >/dev/null 2>&1
printf 'jobs-p:%s\n' "$?"
