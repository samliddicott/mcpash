#!/usr/bin/env ash
# Coverage: deeper command-substitution and quote nesting matrix.
set -eu

v='a b'
out1="$(printf '%s' "$(printf '%s' "$v")")"
printf 'n1=%s\n' "$out1"

out2="$(printf '%s' "x$(printf y)z")"
printf 'n2=%s\n' "$out2"

out3=$((1 + 2))
printf 'n3=%s\n' "$out3"

out4="$(printf '%s' "q r")"
printf 'n4=%s\n' "$out4"
