#!/usr/bin/env ash
# Coverage: threaded runtime cwd isolation for background jobs.
# Areas:
# - background subshell `cd` must not alter parent cwd while running
# - parent cwd remains stable after job completion
set -eu

orig="$(pwd)"
out="/tmp/mctash-thread-cwd-$$.txt"
(
  cd /
  sleep 0.2
  pwd > "$out"
) &
sleep 0.05
mid="$(pwd)"
wait %1
bg="$(cat "$out")"
after="$(pwd)"
rm -f "$out"

printf 'mid=%s\n' "$( [ "$mid" = "$orig" ] && echo same || echo diff )"
printf 'after=%s\n' "$( [ "$after" = "$orig" ] && echo same || echo diff )"
printf 'bg-root=%s\n' "$( [ "$bg" = "/" ] && echo yes || echo no )"
