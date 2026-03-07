#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.046
# Feature: The ‘.’ and ‘source’ builtins do not search the current directory for the filename argument if it is not found by searching ‘PATH’.

echo 'JM:BPOSIX_CORE_046:probe'
