#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: help builtin status surface.
set +e

help echo >/dev/null 2>&1
s1=$?

help __no_such_topic__ >/dev/null 2>&1
s2=$?

help >/dev/null 2>&1
s3=$?

printf 'help:%s,%s,%s\n' "$s1" "$s2" "$s3"
