#!/usr/bin/env ash
# Coverage: read splitting/escape matrix beyond option flags.
# Areas:
# - multi-variable IFS splitting with empty fields
# - raw mode handling with -r
set -e

printf 'a::b\n' | (
  IFS=':'
  read x y z
  printf 'split=%s|%s|%s\n' "$x" "$y" "$z"
)

printf 'a\\ b\n' | (
  IFS=' '
  read -r x y
  printf 'raw=%s|%s\n' "$x" "$y"
)
