#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.52.002: bind -p/-P argument handling.
set +e
out_p="$(bind -p self-insert 2>&1)"; rc_p=$?
out_P="$(bind -P self-insert 2>&1)"; rc_P=$?
set -e
echo "JM:BCOMPAT_52_002:p=$rc_p P=$rc_P"
printf 'JM:BCOMPAT_52_002:op=%s\n' "$out_p"
printf 'JM:BCOMPAT_52_002:oP=%s\n' "$out_P"
