#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 34: special builtin error is fatal in non-interactive shell
echo JM:034:pre
export -Z
# Should not execute if fatal behavior matches
echo JM:034:post

