#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.51.001
# Feature: The `unset' builtin will unset the array a given an argument like `a[@]'. Bash-5.2 will unset an element with key `@' (associative arrays) or remove all the elements without unsetting the array (indexed arrays)

echo 'JM:BCOMPAT_51_001:probe'
