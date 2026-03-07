#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for rows 071..075.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 071 072 073 074 075; do
  . "$CASE_DIR/bash-posix-doc-${n}.sh"
done
