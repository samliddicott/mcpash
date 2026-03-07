#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 73: unsetting an assignment-preceded variable should persist effect.
x073=outer
x073=temp unset x073
if [ "${x073+set}" = set ]; then
  echo "JM:073:set:$x073"
else
  echo 'JM:073:unset'
fi
