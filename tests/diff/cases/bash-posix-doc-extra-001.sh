#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Extra 1: multibyte IFS behavior.
input=$'aa\u00e9bb\u00e9cc'
IFS=$'\u00e9'
set -- $input
printf 'JM:EXTRA001:argc=%s a=%s b=%s c=%s\n' "$#" "${1-}" "${2-}" "${3-}"
