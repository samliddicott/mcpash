#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): declare behavior under explicit BASH_COMPAT gate in mctash policy.

set +e
BASH_COMPAT=50
export BASH_COMPAT

declare -a arr >/dev/null 2>&1
printf 'decl-a:%s\n' "$?"
declare -A map >/dev/null 2>&1
printf 'decl-A:%s\n' "$?"

declare -p arr >/dev/null 2>&1
printf 'decl-pa:%s\n' "$?"
declare -p map >/dev/null 2>&1
printf 'decl-pA:%s\n' "$?"
