#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: fc behavior with empty history after explicit clear.
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
set +e
set -o history
history -c

fc -l -n -1 >/dev/null 2>&1
s_list=$?

fc -e true -1 >/dev/null 2>&1
s_edit=$?

fc -e - -1 >/dev/null 2>&1
s_reexec=$?

fc -s >/dev/null 2>&1
s_sub=$?

printf 'fc-empty-history=%s,%s,%s,%s\n' "$s_list" "$s_edit" "$s_reexec" "$s_sub"
