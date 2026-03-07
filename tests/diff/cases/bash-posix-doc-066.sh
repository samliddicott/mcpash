#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.066
# Feature: The ‘test’ builtin's ‘-t’ unary primary requires an argument. Historical versions of ‘test’ made the argument optional in certain cases, and Bash attempts to accommodate those for backwards compatibility.

echo 'JM:BPOSIX_CORE_066:probe'
