#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - associative declaration and element assignment
# - ${map[key]} fetch
# - ${#map[@]} cardinality
# - ${!map[@]} key expansion (order-normalized)
declare -A map
map[aa]=11
map[bb]=22
map[cc]=33
echo "vals:${map[aa]}:${map[bb]}:${map[cc]} n:${#map[@]}"
printf '%s\n' "${!map[@]}" | sort | tr '\n' ' ' | sed 's/[[:space:]]*$//'
