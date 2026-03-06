#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - TIMEFORMAT variable behavior for `time` output rendering.
# - `%R`, `%U`, `%S`, `%P`, `%%`, and precision forms.

normalize_time_output() {
  sed -E \
    -e 's/[0-9]+(\.[0-9]+)?/NUM/g' \
    -e 's/ +/ /g'
}

run_time_case() {
  fmt="$1"
  out=""
  out="$(
    TIMEFORMAT="$fmt"
    { time true; } 2>&1 >/dev/null
  )"
  printf '%s\n' "$out" | sed -E -e 's/[0-9]+(\.[0-9]+)?/NUM/g' -e 's/ +/ /g'
}

printf 'case:1\n'
run_time_case 'R=%R U=%U S=%S P=%P %%=%%'

printf 'case:2\n'
run_time_case '%9R %9U %9S %9P'
