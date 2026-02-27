#!/usr/bin/env ash
# Coverage: man ash hash, times, ulimit, umask builtins (caching, timing, limit queries).
set -eu
hash -r
hash ls >/dev/null
printf 'hash-status=%s\n' "$?"
times >/dev/null
printf 'times-status=%s\n' "$?"
umask >/dev/null
printf 'umask-status=%s\n' "$?"
ulimit -n >/dev/null
printf 'ulimit-status=%s\n' "$?"
