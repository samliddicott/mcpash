#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.42.001: replacement quote-removal in ${x/pat/repl}.
x='ab'
echo "JM:BCOMPAT_42_001:${x/b/\"Q\"}"
