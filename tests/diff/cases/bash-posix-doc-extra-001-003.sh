#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for EXTRA rows.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 001 002 003; do
  . "$CASE_DIR/bash-posix-doc-extra-${n}.sh"
done
