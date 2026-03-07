#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.41.001
# Feature: in posix mode, `time' may be followed by options and still be recognized as a reserved word (this is POSIX interpretation 267)

echo 'JM:BCOMPAT_41_001:probe'
