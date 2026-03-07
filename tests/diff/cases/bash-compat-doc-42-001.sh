#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.42.001
# Feature: the replacement string in double-quoted pattern substitution is not run through quote removal, as it is in versions after bash-4.2

echo 'JM:BCOMPAT_42_001:probe'
