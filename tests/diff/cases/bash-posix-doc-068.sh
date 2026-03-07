#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.068
# Feature: The ‘trap’ builtin doesn't check the first argument for a possible signal specification and revert the signal handling to the original disposition if it is, unless that argument consists solely of digits and is a valid signal number.  If users want to reset the handler for a given signal to the original disposition, they should use ‘-’ as the first argument.

echo 'JM:BPOSIX_CORE_068:probe'
