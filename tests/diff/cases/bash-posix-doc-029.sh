#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 29: default HISTFILE in POSIX mode.
set +u
echo "JM:029:${HISTFILE-<unset>}"
set -u
