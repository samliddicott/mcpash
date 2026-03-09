#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.52.002: bind -p/-P argument handling.
set +e
out_p="$(bind -p self-insert 2>&1)"; rc_p=$?
out_P="$(bind -P self-insert 2>&1)"; rc_P=$?
set -e
echo "JM:BCOMPAT_52_002:p=$rc_p P=$rc_P"
case "$out_p" in
  *self-insert*) echo 'JM:BCOMPAT_52_002:p_has_self_insert=1' ;;
  *) echo 'JM:BCOMPAT_52_002:p_has_self_insert=0' ;;
esac
case "$out_P" in
  *self-insert*) echo 'JM:BCOMPAT_52_002:P_has_self_insert=1' ;;
  *) echo 'JM:BCOMPAT_52_002:P_has_self_insert=0' ;;
esac
