#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - ${v@P} prompt-style transformation over prompt escapes and promptvars.

set +e

x='\u@\h:\W \$'
printf 'p1:<%s>\n' "${x@P}" | cat -vet

y='${HOME##*/}:\W'
printf 'p2:<%s>\n' "${y@P}" | cat -vet
