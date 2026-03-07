#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 37: readonly for-loop variable should be fatal in non-interactive shell
readonly I37=1
echo JM:037:pre
for I37 in a b; do :; done
echo JM:037:post

