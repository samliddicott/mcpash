#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 40: invalid identifier to export/readonly/unset is fatal
echo JM:040:pre
export 1BAD=2
echo JM:040:post

