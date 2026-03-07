#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.022
# Feature: The message printed by the job control code and builtins when a job exits with a non-zero status is 'Done(status)'.

echo 'JM:BPOSIX_CORE_022:probe'
