#!/usr/bin/env ash
# Coverage: man ash read builtin (IFS splitting, -r raw mode, -n fixed chars, -d delimiter handling).
set -euo pipefail

IFS=',' read first second <<'DATA1'
alpha,beta
DATA1
printf 'split=%s:%s\n' "$first" "$second"

read -r raw_line <<'DATA2'
line with \\backslash
DATA2
printf 'raw=%s\n' "$raw_line"

printf 'ab' | {
  IFS= read -r -n 1 ch1
  read -r -n 1 ch2
  printf 'mostly=%s%s\n' "$ch1" "$ch2"
}

read -r -d ':' before after <<'DATA3'
first:second:rest
DATA3
printf 'delim=%s:%s\n' "$before" "$after"
