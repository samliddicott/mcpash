#!/usr/bin/env ash
# Coverage: threaded runtime fd isolation for background jobs.
# Areas:
# - fd opened in background subshell must not leak into parent shell
set -eu

f="/tmp/mctash-thread-fd-$$.txt"
pre9="$( [ -e /proc/$$/fd/9 ] && echo yes || echo no )"
(
  exec 9>"$f"
  echo bg >&9
) &
wait %1

post9="$( [ -e /proc/$$/fd/9 ] && echo yes || echo no )"
printf 'pre9=%s\n' "$pre9"
printf 'post9=%s\n' "$post9"
printf 'bg=%s\n' "$(cat "$f")"
rm -f "$f"
