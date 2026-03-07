#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.44.003: assignment before export/readonly persists to caller env.
v44='old'
v44='new' export v44
echo "JM:BCOMPAT_44_003:export:$v44"
r44='old'
r44='new' readonly r44
echo "JM:BCOMPAT_44_003:readonly:$r44"
