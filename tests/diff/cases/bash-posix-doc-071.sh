#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 71: ulimit -f/-c units and reporting.
set +e
old_f="$(ulimit -f 2>/dev/null)"; rc_old_f=$?
old_c="$(ulimit -c 2>/dev/null)"; rc_old_c=$?
ulimit -f 1 2>/dev/null; rc_set_f=$?
new_f="$(ulimit -f 2>/dev/null)"; rc_new_f=$?
ulimit -f "$old_f" 2>/dev/null || true
set -e
printf 'JM:071:oldf=%s(%s) oldc=%s(%s) setf=%s newf=%s(%s)\n' \
  "$old_f" "$rc_old_f" "$old_c" "$rc_old_c" "$rc_set_f" "$new_f" "$rc_new_f"
