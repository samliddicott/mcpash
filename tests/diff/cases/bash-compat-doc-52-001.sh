#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.52.001
# Feature: the test builtin uses its historical algorithm for parsing expressions composed of five or more primaries.

echo 'JM:BCOMPAT_52_001:probe'
