#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.003: arithmetic args in [[ ]] operators expansion count.
i=0
declare -a arr=(z)
set +e
[[ -v arr[i++] ]]
rc=$?
set -e
echo "JM:BCOMPAT_51_003:i=$i rc=$rc"
