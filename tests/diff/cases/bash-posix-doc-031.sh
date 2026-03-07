#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 31: type function formatting in POSIX mode
f31(){ :; }
if type f31 | grep -Eq '^function[[:space:]]+f31'; then
  echo JM:031:function_kw
else
  echo JM:031:no_function_kw
fi

