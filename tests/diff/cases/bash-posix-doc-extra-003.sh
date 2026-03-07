#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 extra row probe
# Requirement: BPOSIX.EXTRA.003
# Feature: As noted above, Bash requires the ‘xpg_echo’ option to be enabled for the ‘echo’ builtin to be fully conformant.

echo 'JM:BPOSIX_EXTRA_003:probe'
