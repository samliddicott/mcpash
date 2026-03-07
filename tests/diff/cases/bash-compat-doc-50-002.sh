#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.50.002
# Feature: If the command hash table is empty, bash versions prior to bash-5.1 printed an informational message to that effect even when writing output in a format that can be reused as input (-l). Bash-5.1 suppresses that message if -l is supplied

echo 'JM:BCOMPAT_50_002:probe'
