#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: fc editor selection surface in ash-advertised mode.
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
# Areas:
# - FCEDIT precedence
# - EDITOR fallback
# - -e flag override
set +e
set -o history
echo one >/dev/null
echo two >/dev/null

FCEDIT=true EDITOR=false fc 'echo one' 'echo one' >/dev/null 2>&1
s_fcedit=$?

unset FCEDIT
EDITOR=true fc 'echo two' 'echo two' >/dev/null 2>&1
s_editor=$?

FCEDIT=false EDITOR=false fc -e true 'echo two' 'echo two' >/dev/null 2>&1
s_flag=$?

printf 'fc-editor=%s,%s,%s\n' "$s_fcedit" "$s_editor" "$s_flag"
