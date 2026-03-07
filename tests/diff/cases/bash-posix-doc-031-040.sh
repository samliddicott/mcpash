#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for rows 031..040.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 031 032 033 034 035 036 037 038 039 040; do
  . "$CASE_DIR/bash-posix-doc-${n}.sh"
done
