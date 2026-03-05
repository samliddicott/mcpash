#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: disown core status semantics.
set +e

# no jobs

disown >/dev/null 2>&1
s0=$?

sleep 0.2 &
j1=$!
disown -h %1 >/dev/null 2>&1
s1=$?
disown -h %1 >/dev/null 2>&1
s2=$?

sleep 0.2 &
j2=$!
disown %2 >/dev/null 2>&1
s3=$?
disown %2 >/dev/null 2>&1
s4=$?

wait "$j1" >/dev/null 2>&1
wait "$j2" >/dev/null 2>&1

printf 'dsown:%s,%s,%s,%s,%s\n' "$s0" "$s1" "$s2" "$s3" "$s4"
