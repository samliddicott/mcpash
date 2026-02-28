#!/usr/bin/env ash
# Coverage: nested quote/substitution word parsing.
# Areas:
# - nested command substitution inside double quotes
# - arithmetic expansion in quoted context
# - backtick substitution in quoted context
# - quote-preserving command-sub results
set -eu

x='ab cd'
a="$(echo "q:$x")"
printf 'a=%s\n' "$a"

b="$(echo "$(echo inner)")"
printf 'b=%s\n' "$b"

c="$(echo "$((1 + 2))")"
printf 'c=%s\n' "$c"

d="`echo bt`"
printf 'd=%s\n' "$d"

e="$(echo 'x y')"
printf 'e=%s\n' "$e"
