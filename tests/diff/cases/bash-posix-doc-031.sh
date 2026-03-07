#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.031
# Feature: When printing shell function definitions (e.g., by ‘type’), Bash does not print the ‘function’ reserved word unless necessary.

echo 'JM:BPOSIX_CORE_031:probe'
