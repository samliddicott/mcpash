#!/usr/bin/env ash
# Coverage: man ash jobs/fg/bg builtins (listing, backgrounding, foregrounding, job tokens).
set -eu
sleep 0.5 &
jobs -l >/dev/null
if bg %1 >/dev/null 2>&1; then
  printf 'bg-ok\n'
else
  printf 'bg-fail\n'
fi
if fg %1 >/dev/null 2>&1; then
  printf 'fg-ok\n'
else
  printf 'fg-fail\n'
fi
printf 'job-done\n'
