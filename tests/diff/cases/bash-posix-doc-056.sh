#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 56: fc -s too many args returns failure
set -o history
echo fc56a >/dev/null
echo fc56b >/dev/null
tmp_out="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_out" "$tmp_err"' EXIT
set +e
fc -s a b c >"$tmp_out" 2>"$tmp_err"
rc=$?
set -e
has_err=0
[ -s "$tmp_err" ] && has_err=1
echo "JM:056:rc=$rc has_err=$has_err"
