#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 55: fc extra args error
set -o history
echo fc55a >/dev/null
echo fc55b >/dev/null
tmp_out="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_out" "$tmp_err"' EXIT
set +e
fc 1 2 3 >"$tmp_out" 2>"$tmp_err"
rc=$?
set -e
has_err=0
[ -s "$tmp_err" ] && has_err=1
echo "JM:055:rc=$rc has_err=$has_err"
