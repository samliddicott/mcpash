#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.51.009
# Feature: the ${param[:]=value} word expansion will return VALUE, before any variable-specific transformations have been performed (e.g., converting to lowercase). Bash-5.2 will return the final value assigned to the variable, as POSIX specifies;

echo 'JM:BCOMPAT_51_009:probe'
