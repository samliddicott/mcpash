#!/usr/bin/env ash
# Coverage: threaded runtime variable isolation for background jobs.
# Areas:
# - variable writes in background subshell do not leak to parent
set -eu

X=parent
(
  X=child
  echo "bg:$X"
) &
wait %1
echo "parent:$X"
