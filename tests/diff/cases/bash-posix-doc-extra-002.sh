#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Extra 2: fc editor selection via FCEDIT/EDITOR.
set +e
fc_out="$(FCEDIT= EDITOR=false fc -l 1 1 2>&1)"; rc=$?
set -e
printf 'JM:EXTRA002:rc=%s out=%s\n' "$rc" "$fc_out"
