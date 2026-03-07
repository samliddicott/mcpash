#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.044
# Feature: Enabling POSIX mode has the effect of setting the ‘shift_verbose’ option, so numeric arguments to ‘shift’ that exceed the number of positional parameters will result in an error message.

echo 'JM:BPOSIX_CORE_044:probe'
