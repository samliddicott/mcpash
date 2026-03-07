#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.062
# Feature: The ‘read’ builtin may be interrupted by a signal for which a trap has been set.  If Bash receives a trapped signal while executing ‘read’, the trap handler executes and ‘read’ returns an exit status greater than 128.

echo 'JM:BPOSIX_CORE_062:probe'
