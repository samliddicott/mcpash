#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.063
# Feature: When the ‘set’ builtin is invoked without options, it does not display shell function names and definitions.

echo 'JM:BPOSIX_CORE_063:probe'
