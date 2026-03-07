#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.030
# Feature: The ‘!’ character does not introduce history expansion within a double-quoted string, even if the ‘histexpand’ option is enabled.

echo 'JM:BPOSIX_CORE_030:probe'
