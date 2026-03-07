#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for COMPAT level 40.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 001; do
  . "$CASE_DIR/bash-compat-doc-40-${n}.sh"
done
