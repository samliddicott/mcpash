#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.038
# Feature: Non-interactive shells exit if FILENAME in ‘.’ FILENAME is not found.

echo 'JM:BPOSIX_CORE_038:probe'
