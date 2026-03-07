#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.067
# Feature: The ‘trap’ builtin displays signal names without the leading ‘SIG’.

echo 'JM:BPOSIX_CORE_067:probe'
