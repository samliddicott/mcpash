#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.043
# Feature: Enabling POSIX mode has the effect of setting the ‘inherit_errexit’ option, so subshells spawned to execute command substitutions inherit the value of the ‘-e’ option from the parent shell.  When the ‘inherit_errexit’ option is not enabled, Bash clears the ‘-e’ option in such subshells.

echo 'JM:BPOSIX_CORE_043:probe'
