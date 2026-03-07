#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.033
# Feature: Non-interactive shells exit if a parameter expansion error occurs.

echo 'JM:BPOSIX_CORE_033:probe'
