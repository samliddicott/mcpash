#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.021
# Feature: Bash will not insert a command without the execute bit set into the command hash table, even if it returns it as a (last-ditch) result from a ‘$PATH’ search.

echo 'JM:BPOSIX_CORE_021:probe'
