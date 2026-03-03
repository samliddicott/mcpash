#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - private-use unicode codepoint should remain ordinary data, not internal marker
# - escaped glob chars adjacent to PUA chars stay literal
pua=$(printf '\356\200\201')

v1="*${pua}?"
v2=\*"$pua"\?

printf 'v1-bytes:%s\n' "$(printf '%s' "$v1" | wc -c | tr -d ' ')"
printf 'v2-bytes:%s\n' "$(printf '%s' "$v2" | wc -c | tr -d ' ')"
printf 'v1-sha:%s\n' "$(printf '%s' "$v1" | sha256sum | awk '{print $1}')"
printf 'v2-sha:%s\n' "$(printf '%s' "$v2" | sha256sum | awk '{print $1}')"
