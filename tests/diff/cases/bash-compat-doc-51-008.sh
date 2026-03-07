#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.51.008
# Feature: `test -v', when given an argument of A[@], where A is an existing associative array, will return true if the array has any set elements. Bash-5.2 will look for a key named `@';

echo 'JM:BCOMPAT_51_008:probe'
