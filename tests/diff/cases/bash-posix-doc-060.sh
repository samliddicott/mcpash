#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 60: printf floating conversion mode probe
printf 'JM:060:%s
' "$(printf '%.3f' 1.125)"

