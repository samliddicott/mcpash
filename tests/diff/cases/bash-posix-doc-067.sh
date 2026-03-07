#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 67: `trap -p` prints signal names without SIG prefix.
trap ':' INT TERM
trap -p INT
trap -p TERM
