#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.050
# Feature: When the ‘cd’ builtin cannot change a directory because the length of the pathname constructed from ‘$PWD’ and the directory name supplied as an argument exceeds ‘PATH_MAX’ when canonicalized, ‘cd’ will attempt to use the supplied directory name.

echo 'JM:BPOSIX_CORE_050:probe'
