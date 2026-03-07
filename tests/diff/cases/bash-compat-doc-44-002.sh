#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.44.002
# Feature: a subshell inherits loops from its parent context, so `break' or `continue' will cause the subshell to exit. Bash-5.0 and later reset the loop state to prevent the exit

echo 'JM:BCOMPAT_44_002:probe'
