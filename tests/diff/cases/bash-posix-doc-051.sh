#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.051
# Feature: When the ‘xpg_echo’ option is enabled, Bash does not attempt to interpret any arguments to ‘echo’ as options.  ‘echo’ displays each argument after converting escape sequences.

echo 'JM:BPOSIX_CORE_051:probe'
