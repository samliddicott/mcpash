#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: enable builtin state toggling and disabled dispatch behavior.
set +e

enable -n echo >/dev/null 2>&1
s1=$?

echo hi >/dev/null 2>&1
s2=$?

builtin echo hi >/dev/null 2>&1
s3=$?

command -v echo >/dev/null 2>&1
s4=$?

enable echo >/dev/null 2>&1
s5=$?

echo hi >/dev/null 2>&1
s6=$?

enable -p >/dev/null 2>&1
s7=$?

printf 'en:%s,%s,%s,%s,%s,%s,%s\n' "$s1" "$s2" "$s3" "$s4" "$s5" "$s6" "$s7"
