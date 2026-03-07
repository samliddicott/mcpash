#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.041
# Feature: Assignment statements preceding POSIX special builtins persist in the shell environment after the builtin completes.

echo 'JM:BPOSIX_CORE_041:probe'
