#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.028
# Feature: Prompt expansion enables the POSIX ‘PS1’ and ‘PS2’ expansions of ‘!’ to the history number and ‘!!’ to ‘!’, and Bash performs parameter expansion on the values of ‘PS1’ and ‘PS2’ regardless of the setting of the ‘promptvars’ option.

echo 'JM:BPOSIX_CORE_028:probe'
