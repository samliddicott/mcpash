#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.040
# Feature: Non-interactive shells exit if the ‘export’, ‘readonly’ or ‘unset’ builtin commands get an argument that is not a valid identifier, and they are not operating on shell functions.  These errors force an exit because these are special builtins.

echo 'JM:BPOSIX_CORE_040:probe'
