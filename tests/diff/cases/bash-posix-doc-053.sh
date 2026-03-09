#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 53: fc list output omits modified marker (*).
set -o history
echo fc53a >/dev/null
echo fc53b >/dev/null
echo fc53c >/dev/null
tmp_out="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_out" "$tmp_err"' EXIT
set +e
fc -l -n -3 -1 >"$tmp_out" 2>"$tmp_err"
rc=$?
set -e
star=0
while IFS= read -r line; do
  case "$line" in
    *'*'*) star=1 ;;
  esac
done <"$tmp_out"
echo "JM:053:rc=$rc star=$star"
