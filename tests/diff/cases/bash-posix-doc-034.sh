#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.034
# Feature: If a POSIX special builtin returns an error status, a non-interactive shell exits.  The fatal errors are those listed in the POSIX standard, and include things like passing incorrect options, redirection errors, variable assignment errors for assignments preceding the command name, and so on.

echo 'JM:BPOSIX_CORE_034:probe'
