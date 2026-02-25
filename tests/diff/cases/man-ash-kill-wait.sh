#!/usr/bin/env ash
# Coverage: man ash kill/wait builtins (kill syntax, waiting for killed processes).
set -euo pipefail
sleep 1 &
pid=$!
if kill -0 "$pid"; then
  printf 'kill-alive=%s\n' "$pid"
fi
kill "$pid"
wait_status=0
if ! wait "$pid"; then
  wait_status=$?
fi
printf 'killed-wait=%s\n' "$wait_status"
