#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.032
# Feature: Non-interactive shells exit if a syntax error in an arithmetic expansion results in an invalid expression.

echo 'JM:BPOSIX_CORE_032:probe'
