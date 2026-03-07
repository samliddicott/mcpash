#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.070
# Feature: The ‘type’ and ‘command’ builtins will not report a non-executable file as having been found, though the shell will attempt to execute such a file if it is the only so-named file found in ‘$PATH’.

echo 'JM:BPOSIX_CORE_070:probe'
