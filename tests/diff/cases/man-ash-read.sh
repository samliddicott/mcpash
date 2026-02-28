#!/usr/bin/env ash
# Coverage: man ash read builtin.
# Areas:
# - IFS splitting and trailing-field behavior
# - backslash handling with and without -r
# - stable read semantics shared across ash variants
set -e

IFS=',' read first second <<'DATA1'
alpha,beta
DATA1
printf 'split=%s:%s\n' "$first" "$second"

read -r raw_line <<'DATA2'
line with \\backslash
DATA2
printf 'raw=%s\n' "$raw_line"

IFS=' ' read -r word1 word2 rest <<'DATA3'
one two three
DATA3
printf 'words=%s:%s:%s\n' "$word1" "$word2" "$rest"

# Without -r, backslash-newline is line continuation.
read cooked_line <<'DATA4'
left \
right
DATA4
printf 'cooked=%s\n' "$cooked_line"
