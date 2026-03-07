#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.049
# Feature: When the ‘cd’ builtin is invoked in logical mode, and the pathname constructed from ‘$PWD’ and the directory name supplied as an argument does not refer to an existing directory, ‘cd’ will fail instead of falling back to physical mode.

echo 'JM:BPOSIX_CORE_049:probe'
