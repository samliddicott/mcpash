#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.006: $(( ... )) expansion expression count.
i=0
expr='i+=1'
val=$(( expr ))
echo "JM:BCOMPAT_51_006:val=$val i=$i"
