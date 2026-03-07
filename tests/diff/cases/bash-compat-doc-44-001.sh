#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.44.001
# Feature: the shell sets up the values used by BASH_ARGV and BASH_ARGC so they can expand to the shell's positional parameters even if extended debug mode is not enabled

echo 'JM:BCOMPAT_44_001:probe'
