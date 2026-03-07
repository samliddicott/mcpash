#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.027
# Feature: The ‘vi’ editing mode will invoke the ‘vi’ editor directly when the ‘v’ command is run, instead of checking ‘$VISUAL’ and ‘$EDITOR’.

echo 'JM:BPOSIX_CORE_027:probe'
