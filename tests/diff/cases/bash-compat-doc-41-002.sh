#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash COMPAT delta row probe
# Requirement: BCOMPAT.41.002
# Feature: in posix mode, the parser requires that an even number of single quotes occur in the `word' portion of a double-quoted ${...} parameter expansion and treats them specially, so that characters within the single quotes are considered quoted (this is POSIX interpretation 221)

echo 'JM:BCOMPAT_41_002:probe'
