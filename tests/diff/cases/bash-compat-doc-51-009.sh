#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.51.009: ${param:=value} returns pre/post transformed value.
declare -l v51
unset v51
echo "JM:BCOMPAT_51_009:exp=${v51:=ABC}:var=$v51"
