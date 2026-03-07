#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.053
# Feature: When listing the history, the ‘fc’ builtin does not include an indication of whether or not a history entry has been modified.

echo 'JM:BPOSIX_CORE_053:probe'
