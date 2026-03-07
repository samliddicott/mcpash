#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.001: unset A[@] behavior for indexed/assoc arrays.
declare -a ia=(x y)
declare -A aa=([@]=at [k]=v)
unset 'ia[@]'
unset 'aa[@]'
set +u
ia_n="${#ia[@]}"
aa_k="${aa[k]-<unset>}"
ok=0
if [ "$ia_n" -eq 0 ] && [ "$aa_k" = "<unset>" ]; then
  ok=1
fi
printf 'JM:BCOMPAT_51_001:ok=%s ia_n=%s aa_k=%s\n' "$ok" "$ia_n" "$aa_k"
set -u
