#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.52.002
# Feature: the -p and -P options to the bind builtin treat remaining arguments as bindable command names for which to print any key bindings

echo 'JM:BCOMPAT_52_002:probe'
