#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 54: default fc editor row probe.
# Use `-e -` to avoid launching an interactive editor under harness; compare
# comparator status semantics for this lane.
set +e
unset FCEDIT EDITOR VISUAL
fc -e - -1 >/tmp/fc54.out 2>/tmp/fc54.err
rc=$?
set -e
echo "JM:054:rc=$rc"
rm -f /tmp/fc54.out /tmp/fc54.err
