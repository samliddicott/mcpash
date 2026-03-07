#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 33: parameter expansion error is fatal in non-interactive shell
echo JM:033:pre
unset X33
: "${X33?err33}"
echo JM:033:post

