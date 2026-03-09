#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: fc reference precedence (numeric ref vs prefix ref).
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
# Areas:
# - all-digit ref token is treated as event number (not prefix)
# - non-digit ref token uses prefix lookup
set +e
set -o history
history -c
history -s '123abc'
history -s 'echo ok'

t1="$(mktemp)"
t2="$(mktemp)"
trap '/bin/rm -f "$t1" "$t2"' EXIT

fc -l -n 123 >"$t1" 2>/dev/null
s_num=$?
num_has=0
[ -s "$t1" ] && num_has=1

fc -l -n 123a >"$t2" 2>/dev/null
s_pref=$?
pref_has=0
[ -s "$t2" ] && pref_has=1

printf 'fc-ref-precedence=%s,%s,%s,%s\n' "$s_num" "$num_has" "$s_pref" "$pref_has"
