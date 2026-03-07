#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.024
# Feature: If the shell is interactive, Bash does not perform job notifications between executing commands in lists separated by ‘;’ or newline.  Non-interactive shells print status messages after a foreground job in a list completes.

echo 'JM:BPOSIX_CORE_024:probe'
