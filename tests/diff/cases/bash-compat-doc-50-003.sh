#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.50.003
# Feature: Bash-5.1 and later use pipes for here-documents and here-strings if they are smaller than the pipe capacity. If the shell compatibility level is set to 50 or lower, it reverts to using temporary files.

echo 'JM:BCOMPAT_50_003:probe'
