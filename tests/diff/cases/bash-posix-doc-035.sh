#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 35: assignment error with no command name is fatal
readonly R35=1
echo JM:035:pre
R35=2
echo JM:035:post

