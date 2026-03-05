#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): history/suspend/logout non-login paths.

set +e

history -c
history -s 'echo alpha'
history -s 'echo beta'
history 2 | sed 's/^[[:space:]]*[0-9][0-9]*[[:space:]]*//'

history -d 1
history 1 | sed 's/^[[:space:]]*[0-9][0-9]*[[:space:]]*//'

tmp_hist="/tmp/mctash-hist-$$"
history -w "$tmp_hist"
history -c
history -r "$tmp_hist"
history 1 | sed 's/^[[:space:]]*[0-9][0-9]*[[:space:]]*//'
rm -f "$tmp_hist"

suspend >/dev/null 2>&1
echo "suspend:$?"

logout >/dev/null 2>&1
echo "logout:$?"
