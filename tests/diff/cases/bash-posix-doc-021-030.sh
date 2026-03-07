#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for rows 021..030.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 021 022 023 024 025 026 027 028 029 030; do
  . "$CASE_DIR/bash-posix-doc-${n}.sh"
done
