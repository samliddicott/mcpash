#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.058
# Feature: The ‘kill’ builtin does not accept signal names with a ‘SIG’ prefix.

echo 'JM:BPOSIX_CORE_058:probe'
