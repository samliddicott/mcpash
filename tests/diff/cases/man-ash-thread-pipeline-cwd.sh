#!/usr/bin/env ash
# Coverage: threaded runtime cwd isolation with background pipeline.
# Areas:
# - cwd changes in a background pipeline must not affect parent cwd
set -eu

orig="$(pwd)"
out="/tmp/mctash-thread-pipe-cwd-$$.txt"
(
  cd /
  pwd
) | cat > "$out" &
sleep 0.05
mid="$(pwd)"
wait %1
bg="$(cat "$out")"
after="$(pwd)"
rm -f "$out"

printf 'mid=%s\n' "$( [ "$mid" = "$orig" ] && echo same || echo diff )"
printf 'after=%s\n' "$( [ "$after" = "$orig" ] && echo same || echo diff )"
printf 'bg-root=%s\n' "$( [ "$bg" = "/" ] && echo yes || echo no )"
