#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.048
# Feature: The ‘bg’ builtin uses the required format to describe each job placed in the background, which does not include an indication of whether the job is the current or previous job.

echo 'JM:BPOSIX_CORE_048:probe'
