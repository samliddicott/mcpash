#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for rows 061..070.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 061 062 063 064 065 066 067 068 069 070; do
  . "$CASE_DIR/bash-posix-doc-${n}.sh"
done
