#!/usr/bin/env ash
# Coverage: threaded runtime fd isolation with background pipeline.
# Areas:
# - fd opened in background pipeline command does not leak to parent
set -eu

f="/tmp/mctash-thread-pipe-fd-$$.txt"
pre9="$( [ -e /proc/$$/fd/9 ] && echo yes || echo no )"
(
  exec 9>"$f"
  echo pipebg >&9
) | cat >/dev/null &
wait %1
post9="$( [ -e /proc/$$/fd/9 ] && echo yes || echo no )"

printf 'pre9=%s\n' "$pre9"
printf 'post9=%s\n' "$post9"
printf 'bg=%s\n' "$(cat "$f")"
rm -f "$f"
