#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.055
# Feature: ‘fc’ treats extra arguments as an error instead of ignoring them.

echo 'JM:BPOSIX_CORE_055:probe'
