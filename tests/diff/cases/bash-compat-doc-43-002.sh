#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.43.002
# Feature: when executing a shell function, the loop state (while/until/etc.) is not reset, so `break' or `continue' in that function will break or continue loops in the calling context. Bash-4.4 and later reset the loop state to prevent this

echo 'JM:BCOMPAT_43_002:probe'
