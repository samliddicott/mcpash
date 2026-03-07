#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.037
# Feature: A non-interactive shell exits with an error status if the iteration variable in a ‘for’ statement or the selection variable in a ‘select’ statement is a readonly variable or has an invalid name.

echo 'JM:BPOSIX_CORE_037:probe'
