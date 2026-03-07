#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.50.001: RANDOM sequence when seeded.
RANDOM=17
echo "JM:BCOMPAT_50_001:${RANDOM},${RANDOM},${RANDOM},${RANDOM}"
