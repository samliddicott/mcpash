#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: fc range/reference semantics advertised in ash man page.
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
# Areas:
# - negative history range listing
# - reverse listing over range
# - list range semantics only (error-status differences tracked in mctash regressions)
set +e
set -o history
echo one >/dev/null
echo two >/dev/null
echo three >/dev/null
echo four >/dev/null

fc -l -n -4 -2 >/dev/null 2>&1
s_range=$?

fc -l -r -n -4 -2 >/dev/null 2>&1
s_range_rev=$?

printf 'fc-range=%s,%s\n' "$s_range" "$s_range_rev"
