#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 39: syntax error in eval/source fatal in non-interactive shell
echo JM:039:pre
eval 'if then'
echo JM:039:post

