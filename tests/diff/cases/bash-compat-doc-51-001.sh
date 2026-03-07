#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.001: unset A[@] behavior for indexed/assoc arrays.
declare -a ia=(x y)
declare -A aa=([@]=at [k]=v)
unset 'ia[@]'
unset 'aa[@]'
printf 'JM:BCOMPAT_51_001:ia_n=%s aa_at=%s aa_k=%s\n' \
  "${#ia[@]}" "${aa[@]-<unset>}" "${aa[k]-<unset>}"
