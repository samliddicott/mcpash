#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 core row probe
# Requirement: BPOSIX.CORE.059
# Feature: The ‘kill’ builtin returns a failure status if any of the pid or job arguments are invalid or if sending the specified signal to any of them fails.  In default mode, ‘kill’ returns success if the signal was successfully sent to any of the specified processes.

echo 'JM:BPOSIX_CORE_059:probe'
