#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Extra 1: multibyte IFS behavior.
input='aaébbécc'
IFS='é'
set -- $input
printf 'JM:EXTRA001:argc=%s a=%s b=%s c=%s\n' "$#" "${1-}" "${2-}" "${3-}"
