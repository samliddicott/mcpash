#!/usr/bin/env ash
# Coverage: man ash read builtin (IFS splitting, -r raw mode, -n fixed chars, -d delimiter handling).
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
