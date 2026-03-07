#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.069
# Feature: ‘trap -p’ without arguments displays signals whose dispositions are set to SIG_DFL and those that were ignored when the shell started, not just trapped signals.

echo 'JM:BPOSIX_CORE_069:probe'
