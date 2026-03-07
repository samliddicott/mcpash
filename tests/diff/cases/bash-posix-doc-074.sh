#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.074
# Feature: The arrival of ‘SIGCHLD’ when a trap is set on ‘SIGCHLD’ does not interrupt the ‘wait’ builtin and cause it to return immediately. The trap command is run once for each child that exits.

echo 'JM:BPOSIX_CORE_074:probe'
