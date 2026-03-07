#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.52.003
# Feature: interactive shells will notify the user of completed jobs while sourcing a script. Newer versions defer notification until script execution completes.

echo 'JM:BCOMPAT_52_003:probe'
