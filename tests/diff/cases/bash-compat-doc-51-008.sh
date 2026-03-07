#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.008: test -v A[@] semantics for associative arrays.
declare -A a=([k]=v)
set +e
[ -v 'a[@]' ]; rc1=$?
unset 'a[k]'
[ -v 'a[@]' ]; rc2=$?
set -e
echo "JM:BCOMPAT_51_008:rc1=$rc1 rc2=$rc2"
