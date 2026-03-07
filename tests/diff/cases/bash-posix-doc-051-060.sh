#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for rows 051..060.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 051 052 053 054 055 056 057 058 059 060; do
  . "$CASE_DIR/bash-posix-doc-${n}.sh"
done
