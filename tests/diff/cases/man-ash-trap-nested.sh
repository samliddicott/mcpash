#!/usr/bin/env ash
# Coverage: nested trap interaction behavior.
# Areas:
# - trap action installs another trap
# - nested signal dispatch executes in-process handlers
set -eu

trap 'echo outer; trap "echo inner" INT; kill -INT $$; echo after-int' TERM
kill -TERM $$
printf 'done\n'
