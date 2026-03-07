#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 36: assignment error before non-special command is non-fatal;
# before special builtin is fatal.
readonly R36=1
R36=2 true || true
echo JM:036:after_true
R36=3 export Y36=1
echo JM:036:after_export

