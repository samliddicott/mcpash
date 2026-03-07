#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.023
# Feature: The message printed by the job control code and builtins when a job is stopped is 'Stopped(SIGNAME)', where SIGNAME is, for example, ‘SIGTSTP’.

echo 'JM:BPOSIX_CORE_023:probe'
