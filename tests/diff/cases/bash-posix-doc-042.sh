#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.042
# Feature: The ‘command’ builtin does not prevent builtins that take assignment statements as arguments from expanding them as assignment statements; when not in POSIX mode, declaration commands lose their assignment statement expansion properties when preceded by ‘command’.

echo 'JM:BPOSIX_CORE_042:probe'
