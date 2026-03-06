#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): JOB CONTROL jobspec prefix (`%name`) and substring (`%?text`) matching + ambiguity.

set +e

/bin/sleep 0.4 &
sleep 0.5 &
wait %/bin/sl >/dev/null 2>&1
printf 'prefix:%s\n' "$?"

sleep 0.4 &
sleep 0.5 &
wait %?0.5 >/dev/null 2>&1
printf 'substr:%s\n' "$?"

sleep 0.5 &
sleep 0.6 &
wait %?sleep >/dev/null 2>&1
printf 'ambig:%s\n' "$?"

wait >/dev/null 2>&1
