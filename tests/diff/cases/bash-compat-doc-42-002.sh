#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.42.002
# Feature: in posix mode, single quotes are considered special when expanding the `word' portion of a double-quoted ${...} parameter expansion and can be used to quote a closing brace or other special character (this is part of POSIX interpretation 221); in later versions, single quotes are not special within double-quoted word expansions

echo 'JM:BCOMPAT_42_002:probe'
