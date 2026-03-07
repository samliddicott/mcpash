#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.061
# Feature: The ‘pwd’ builtin verifies that the value it prints is the same as the current directory, even if it is not asked to check the file system with the ‘-P’ option.

echo 'JM:BPOSIX_CORE_061:probe'
