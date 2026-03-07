#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.51.003
# Feature: expressions used as arguments to arithmetic operators in the [[ conditional command can be expanded more than once

echo 'JM:BCOMPAT_51_003:probe'
