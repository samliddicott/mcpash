#!/usr/bin/env ash
# Coverage: man ash jobs/fg/bg builtins.
# Areas:
# - monitor-mode off failure diagnostics via status
# - listing modes `jobs`, `jobs -l`, `jobs -p`
# - `%` job token wait behavior
set -eu

sleep 0.2 &
jobs >/dev/null
jobs -l >/dev/null
pids="$(jobs -p | wc -w | tr -d ' ')"
printf 'jobs-p=%s\n' "$pids"

set +e
bg %1 >/dev/null 2>&1
bg_status=$?
fg %1 >/dev/null 2>&1
fg_status=$?
set -e
printf 'bg-status=%s\n' "$bg_status"
printf 'fg-status=%s\n' "$fg_status"

wait %1
printf 'job-done\n'
