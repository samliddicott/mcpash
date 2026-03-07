#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 68: `trap` first argument parsing (numeric reset vs command string).
trap 'echo old' TERM
trap INT TERM
trap -p TERM
trap - TERM
trap -p TERM
