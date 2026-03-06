#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): JOB CONTROL jobspec core forms (`%%`, `%+`, bare `%`, `%-`).

set +e

sleep 0.2 &
sleep 0.3 &
wait %% >/dev/null 2>&1
printf 'w%%:%s\n' "$?"

sleep 0.2 &
sleep 0.3 &
wait %+ >/dev/null 2>&1
printf 'w+:%s\n' "$?"

sleep 0.2 &
sleep 0.3 &
wait % >/dev/null 2>&1
printf 'wbare:%s\n' "$?"

sleep 0.2 &
sleep 0.3 &
wait %- >/dev/null 2>&1
printf 'w-:%s\n' "$?"

wait >/dev/null 2>&1
