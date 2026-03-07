#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.035
# Feature: A non-interactive shell exits with an error status if a variable assignment error occurs when no command name follows the assignment statements.  A variable assignment error occurs, for example, when trying to assign a value to a readonly variable.

echo 'JM:BPOSIX_CORE_035:probe'
