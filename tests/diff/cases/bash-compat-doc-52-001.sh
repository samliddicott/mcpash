#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.52.001: `test` parsing algorithm for complex expressions.
set +e
test 1 -eq 1 -a 2 -eq 2 -o 3 -eq 4
rc1=$?
test \( 1 -eq 1 -a 2 -eq 2 \) -o 3 -eq 4
rc2=$?
set -e
echo "JM:BCOMPAT_52_001:rc1=$rc1 rc2=$rc2"
