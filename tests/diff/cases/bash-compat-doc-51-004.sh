#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.004: [[ -v A[subscript] ]] subscript expansion count.
i=0
declare -A aa=([0]=x)
set +e
[[ -v aa[i++] ]]
rc=$?
set -e
echo "JM:BCOMPAT_51_004:i=$i rc=$rc"
