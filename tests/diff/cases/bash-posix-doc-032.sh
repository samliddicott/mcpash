#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 32: arithmetic syntax error in non-interactive shell is fatal
echo JM:032:pre
: $((1+))
echo JM:032:post

