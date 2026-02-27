#!/usr/bin/env ash
# Coverage: man ash kill/wait builtins (kill syntax, waiting for killed processes).
set -eu
sleep 1 &
pid=$!
if kill -0 "$pid"; then
  printf 'kill-alive\n'
fi
wait "$pid"
printf 'wait-status=%s\n' "$?"
