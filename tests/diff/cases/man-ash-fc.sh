#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: man ash-advertised `fc` operations, using bash comparator because ash lacks fc.
# Areas:
# - list mode with -l/-n
# - reverse listing with -r
# - edit mode surface with -e
# - substitution replay with -s and old=new
set +e
set -o history
echo alpha >/dev/null
echo beta >/dev/null
echo gamma >/dev/null
fc -l -n -3 -2 >/dev/null 2>&1
s_list=$?
fc -l -r -n -3 -2 >/dev/null 2>&1
s_rev=$?
fc -e true -3 -2 >/dev/null 2>&1
s_edit=$?
fc -s 'beta=BETA' 'echo beta' >/dev/null 2>&1
s_sub1=$?
fc -s 'alpha=ALPHA' 'echo alpha' >/dev/null 2>&1
s_sub2=$?
printf 'fc-status=%s,%s,%s,%s,%s\n' "$s_list" "$s_rev" "$s_edit" "$s_sub1" "$s_sub2"
