#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.057
# Feature: The output of ‘kill -l’ prints all the signal names on a single line, separated by spaces, without the ‘SIG’ prefix.

echo 'JM:BPOSIX_CORE_057:probe'
