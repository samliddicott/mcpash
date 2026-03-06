#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - BASH_XTRACEFD routes xtrace output away from stderr when set to a valid FD.

tmp="$(mktemp)"
exec 9>"$tmp"
BASH_XTRACEFD=9

set -x
echo TRACE_MARK
set +x

exec 9>&-

printf 'trace-file:'
tr '\n' ';' <"$tmp"
printf '\n'
printf 'stderr-done\n'

rm -f "$tmp"
