#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.071
# Feature: The ‘ulimit’ builtin uses a block size of 512 bytes for the ‘-c’ and ‘-f’ options.

echo 'JM:BPOSIX_CORE_071:probe'
