#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.065
# Feature: The ‘test’ builtin compares strings using the current locale when evaluating the ‘<’ and ‘>’ binary operators.

echo 'JM:BPOSIX_CORE_065:probe'
