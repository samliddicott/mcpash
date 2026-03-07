#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.073
# Feature: When asked to unset a variable that appears in an assignment statement preceding the command, the ‘unset’ builtin attempts to unset a variable of the same name in the current or previous scope as well.  This implements the required "if an assigned variable is further modified by the utility, the modifications made by the utility shall persist" behavior.

echo 'JM:BPOSIX_CORE_073:probe'
