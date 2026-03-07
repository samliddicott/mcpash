#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 38: dot/source missing file fatal in non-interactive shell
echo JM:038:pre
. /definitely/not/here/missing.sh
echo JM:038:post

