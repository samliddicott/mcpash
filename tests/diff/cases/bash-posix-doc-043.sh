#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 43: inherit_errexit in command substitution under posix mode
set -e
if out43="$(false; echo should_not_print)"; then
  echo JM:043:ok:${out43}
else
  echo JM:043:fail
fi

