#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 41: assignment preceding special builtin persists
unset A41
A41=hello export A41
echo JM:041:${A41}

