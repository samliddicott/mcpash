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
  local fmt="$1"
  local out
  out="$(
    TIMEFORMAT="$fmt"
    { time true; } 2>&1 >/dev/null
  )"
  printf '%s\n' "$out" | normalize_time_output
}

printf 'case:1\n'
run_time_case 'R=%R U=%U S=%S P=%P %%=%%'

printf 'case:2\n'
run_time_case '%9R %9U %9S %9P'
