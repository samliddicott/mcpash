#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.51.006
# Feature: the expressions in the $(( ... )) word expansion can be expanded more than once

echo 'JM:BCOMPAT_51_006:probe'
