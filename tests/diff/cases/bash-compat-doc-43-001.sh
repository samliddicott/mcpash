#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.43.001
# Feature: word expansion errors are considered non-fatal errors that cause the current command to fail, even in posix mode (the default behavior is to make them fatal errors that cause the shell to exit)

echo 'JM:BCOMPAT_43_001:probe'
