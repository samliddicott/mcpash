#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.056
# Feature: If there are too many arguments supplied to ‘fc -s’, ‘fc’ prints an error message and returns failure.

echo 'JM:BPOSIX_CORE_056:probe'
