#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.072
# Feature: The ‘unset’ builtin with the ‘-v’ option specified returns a fatal error if it attempts to unset a ‘readonly’ or ‘non-unsettable’ variable, which causes a non-interactive shell to exit.

echo 'JM:BPOSIX_CORE_072:probe'
