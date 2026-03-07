#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.005: substring expansion expression expansion count.
i=0
s=abcdef
out="${s:i++:1}"
echo "JM:BCOMPAT_51_005:out=$out i=$i"
