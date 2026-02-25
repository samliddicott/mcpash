#!/usr/bin/env ash
# Coverage: man ash hash, times, ulimit, umask builtins (caching, timing, limit queries).
set -euo pipefail
hash -r
hash ls >/dev/null
hash

times
umask
ulimit -n
