#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.075
# Feature: Bash removes an exited background process's status from the list of such statuses after the ‘wait’ builtin returns it.

echo 'JM:BPOSIX_CORE_075:probe'
