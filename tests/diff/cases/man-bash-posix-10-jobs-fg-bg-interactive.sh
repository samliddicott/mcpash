#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): jobs/fg/bg non-interactive baseline behavior.

set +e
sleep 0.1 &

jobs >/dev/null 2>&1
printf 'jobs:%s\n' "$?"

bg %1 >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
  echo 'bg:nonzero'
else
  echo 'bg:zero'
fi

fg %1 >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
  echo 'fg:nonzero'
else
  echo 'fg:zero'
fi

wait %1 >/dev/null 2>&1
printf 'wait:%s\n' "$?"
