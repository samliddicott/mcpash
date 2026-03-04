#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): read/test/trap/kill/wait

set +e
printf 'a b\n' | { read v1 v2; printf 'read:%s:%s\n' "$v1" "$v2"; }

if test -n "abc"; then
  echo 'test:true'
else
  echo 'test:false'
fi

trap 'echo trap:USR1' USR1
( kill -USR1 $$ ) >/dev/null 2>&1
sleep 0.1
trap - USR1

sleep 0.2 &
pid=$!
wait "$pid"
printf 'wait:%s\n' "$?"

kill -0 "$pid" >/dev/null 2>&1
printf 'kill0-after:%s\n' "$?"
