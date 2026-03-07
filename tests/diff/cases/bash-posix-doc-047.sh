#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.047
# Feature: When the ‘alias’ builtin displays alias definitions, it does not display them with a leading ‘alias ’ unless the ‘-p’ option is supplied.

echo 'JM:BPOSIX_CORE_047:probe'
