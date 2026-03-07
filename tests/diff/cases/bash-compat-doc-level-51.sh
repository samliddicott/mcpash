#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Aggregated semantic probe for COMPAT level 51.
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
for n in 001 002 003 004 005 006 007 008 009 010; do
  . "$CASE_DIR/bash-compat-doc-51-${n}.sh"
done
