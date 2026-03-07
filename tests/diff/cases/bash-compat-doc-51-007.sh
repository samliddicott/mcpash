#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.007: indexed array subscript arithmetic expansion count.
i=0
declare -a a=(x y)
out="${a[i++]}"
echo "JM:BCOMPAT_51_007:out=$out i=$i"
