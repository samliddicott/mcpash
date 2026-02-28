#!/usr/bin/env ash
# Coverage: set -m monitor-mode behavior in non-interactive shell.
# Areas:
# - enabling monitor mode without tty
# - jobs/bg/fg statuses in monitor-off state
set -eu

set +e
set -m >/dev/null 2>/dev/null
st_setm=$?
jobs -p >/dev/null 2>&1
st_jobs=$?
bg %1 >/dev/null 2>&1
st_bg=$?
fg %1 >/dev/null 2>&1
st_fg=$?
set -e

printf 'set-m=%s\n' "$st_setm"
printf 'jobs-p=%s\n' "$st_jobs"
printf 'bg=%s\n' "$st_bg"
printf 'fg=%s\n' "$st_fg"
