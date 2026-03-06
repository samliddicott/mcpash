#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): JOB CONTROL `%jobspec` and `%jobspec &` command forms in non-interactive lane.

set +e
exec 2>/dev/null

sleep 0.2 &
%1 >/dev/null 2>&1
if [ "$?" -ne 0 ]; then
  echo 'pct_fg:nz'
else
  echo 'pct_fg:z'
fi

sleep 0.2 &
%1 &>/dev/null
if [ "$?" -ne 0 ]; then
  echo 'pct_bg:nz'
else
  echo 'pct_bg:z'
fi

wait >/dev/null 2>&1
