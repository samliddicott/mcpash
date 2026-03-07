#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for rows 041..050.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 041 042 043 044 045 046 047 048 049 050; do
  . "$CASE_DIR/bash-posix-doc-${n}.sh"
done
