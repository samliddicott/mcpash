#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.026
# Feature: Bash permanently removes jobs from the jobs table after notifying the user of their termination via the ‘wait’ or ‘jobs’ builtins. It removes the job from the jobs list after notifying the user of its termination, but the status is still available via ‘wait’, as long as ‘wait’ is supplied a PID argument.

echo 'JM:BPOSIX_CORE_026:probe'
