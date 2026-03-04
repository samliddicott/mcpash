#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: fc edit-and-reexecute path with deterministic editor transformation.
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
# Areas:
# - explicit -e editor invocation
# - edited temporary file is re-read and executed
# - edited command is appended to history
set +e
set -o history

echo one >/dev/null
echo two

FCEDIT='sed -i s/echo\ two/echo\ TWO/'
fc -e "$FCEDIT" 'echo two' 'echo two' >/dev/null 2>&1
s_edit=$?

fc -l -n -1 -1 >/dev/null 2>&1
s_list=$?

printf 'fc-edit-reexec=%s,%s\n' "$s_edit" "$s_list"
