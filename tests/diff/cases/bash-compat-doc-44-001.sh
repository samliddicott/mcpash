#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.44.001: BASH_ARGV/BASH_ARGC visibility without extdebug.
shopt -u extdebug || true
set -- aa bb cc
echo "JM:BCOMPAT_44_001:ARGC=${BASH_ARGC[*]-<unset>}"
echo "JM:BCOMPAT_44_001:ARGV=${BASH_ARGV[*]-<unset>}"
