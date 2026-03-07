#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.002: arithmetic command expression may expand more than once.
i=0
expr='i+=1'
(( $expr ))
echo "JM:BCOMPAT_51_002:i=$i"
