#!/usr/bin/env ash
# Coverage: man ash jobs/fg/bg builtins (listing, backgrounding, foregrounding, job tokens).
set -euo pipefail
sleep 0.5 &
job_pid=$!
jobs -l
bg %1 >/dev/null
fg %1 >/dev/null
printf 'job-done=%s\n' "$job_pid"
