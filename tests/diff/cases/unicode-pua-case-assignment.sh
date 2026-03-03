#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - assignment with escaped glob chars adjacent to private-use unicode
# - case matching with quoted/unquoted patterns including private-use char
pua=""

a="\\*${pua}\\?"
b="z${pua}k"

printf 'a-sha:%s\n' "$(printf '%s' "$a" | sha256sum | awk '{print $1}')"
printf 'b-sha:%s\n' "$(printf '%s' "$b" | sha256sum | awk '{print $1}')"

case "$b" in
  *"$pua"*) echo case-q:yes ;;
  *) echo case-q:no ;;
esac

case "$b" in
  *$pua*) echo case-u:yes ;;
  *) echo case-u:no ;;
esac
