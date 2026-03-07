#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 63: `set` output in POSIX mode should not include function definitions.
f63() { :; }
if set | grep -Eq '^f63[[:space:]]*\(\)'; then
  echo JM:063:function-listed
else
  echo JM:063:function-hidden
fi
