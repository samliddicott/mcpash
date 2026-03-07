#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 69: `trap -p` without args includes default/ignored dispositions.
trap -p | sed -n '1,12p'
