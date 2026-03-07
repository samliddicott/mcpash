#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 42: command + declaration command assignment behavior in POSIX mode
unset D42
command export D42=ok
echo JM:042:${D42}

