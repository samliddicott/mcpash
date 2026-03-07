#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 72: unset -v readonly should be fatal in non-interactive shell.
readonly V072=1
unset -v V072
# If this prints, fatal behavior did not occur.
echo JM:072:continued
