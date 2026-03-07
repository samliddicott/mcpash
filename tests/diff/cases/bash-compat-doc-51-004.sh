#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.51.004
# Feature: indexed and associative array subscripts used as arguments to the operators in the [[ conditional command (e.g., `[[ -v') can be expanded more than once. Bash-5.2 behaves as if the `assoc_expand_once' option were enabled.

echo 'JM:BCOMPAT_51_004:probe'
