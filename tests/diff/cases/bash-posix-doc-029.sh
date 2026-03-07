#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.029
# Feature: The default history file is ‘~/.sh_history’ (this is the default value the shell assigns to ‘$HISTFILE’).

echo 'JM:BPOSIX_CORE_029:probe'
