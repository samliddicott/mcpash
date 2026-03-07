#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.060
# Feature: The ‘printf’ builtin uses ‘double’ (via ‘strtod’) to convert arguments corresponding to floating point conversion specifiers, instead of ‘long double’ if it's available.  The ‘L’ length modifier forces ‘printf’ to use ‘long double’ if it's available.

echo 'JM:BPOSIX_CORE_060:probe'
