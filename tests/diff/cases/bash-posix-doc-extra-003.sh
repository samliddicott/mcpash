#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Extra 3: xpg_echo controls POSIX echo conformance behavior.
shopt -u xpg_echo || true
echo "JM:EXTRA003:off:$(echo '\\141')"
shopt -s xpg_echo || true
echo "JM:EXTRA003:on:$(echo '\\141')"
