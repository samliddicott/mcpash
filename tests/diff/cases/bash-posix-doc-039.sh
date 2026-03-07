#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.039
# Feature: Non-interactive shells exit if there is a syntax error in a script read with the ‘.’ or ‘source’ builtins, or in a string processed by the ‘eval’ builtin.

echo 'JM:BPOSIX_CORE_039:probe'
