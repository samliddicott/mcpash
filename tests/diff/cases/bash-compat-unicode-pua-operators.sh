#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - parameter-operator behavior with literal private-use unicode chars
# - ensure private-use chars are treated as ordinary user data
pua=$(printf '\356\200\201')
x="aa${pua}bb${pua}cc"

r1=${x#*${pua}}
r2=${x%${pua}*}
r3=${x/${pua}/X}
r4=${x//${pua}/Y}

printf 'x-len:%s\n' "$(printf '%s' "$x" | wc -c | tr -d ' ')"
printf 'r1-sha:%s\n' "$(printf '%s' "$r1" | sha256sum | awk '{print $1}')"
printf 'r2-sha:%s\n' "$(printf '%s' "$r2" | sha256sum | awk '{print $1}')"
printf 'r3-sha:%s\n' "$(printf '%s' "$r3" | sha256sum | awk '{print $1}')"
printf 'r4-sha:%s\n' "$(printf '%s' "$r4" | sha256sum | awk '{print $1}')"
