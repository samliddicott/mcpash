#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 extra row probe
# Requirement: BPOSIX.EXTRA.002
# Feature: The ‘fc’ builtin checks ‘$EDITOR’ as a program to edit history entries if ‘FCEDIT’ is unset, rather than defaulting directly to ‘ed’.  ‘fc’ uses ‘ed’ if ‘EDITOR’ is unset.

echo 'JM:BPOSIX_EXTRA_002:probe'
