#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 46: dot/source should not search cwd when PATH lookup fails
tmp46="$(mktemp -d)"; trap 'rm -rf "$tmp46"' EXIT
cd "$tmp46"
printf 'echo BAD46
' > localdot
set +e
. localdot >/dev/null 2>&1
st=$?
set -e
echo JM:046:${st}

