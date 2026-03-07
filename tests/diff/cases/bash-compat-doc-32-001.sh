#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.32.001
# Feature: the < and > operators to the [[ command do not consider the current locale when comparing strings; they use ASCII ordering

echo 'JM:BCOMPAT_32_001:probe'
