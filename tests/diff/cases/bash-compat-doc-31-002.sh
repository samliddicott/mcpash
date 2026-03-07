#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.31.002
# Feature: quoting the rhs of the [[ command's regexp matching operator (=~) has no special effect

echo 'JM:BCOMPAT_31_002:probe'
