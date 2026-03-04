#!/usr/bin/env ash
# Coverage: deep nested quote/substitution combinations.
# Areas:
# - nested $(...) and backticks across quote boundaries
# - arithmetic inside command substitution and nested double quotes
# - parameter expansion operators inside quoted command substitutions
# - adjacency of quoted and unquoted word parts

set -eu

X='a b'
Y='z'

v1="$(printf '%s' "$(printf '%s' "${X% *}")")"
printf 'n1:%s\n' "$v1"

v2="$(printf '%s:%s' "$(printf '%s' "${X#* }")" "$Y")"
printf 'n2:%s\n' "$v2"

v3="$(printf '%s' "$((1 + 2))")"
printf 'n3:%s\n' "$v3"

v4="pre$(printf '%s' "$(printf '%s' mid)")post"
printf 'n4:%s\n' "$v4"

v5="$(printf '%s' "`printf '%s' bt`")"
printf 'n5:%s\n' "$v5"

unset U || true
v6="$(printf '<%s>' "${U:-$(printf '%s' def)}")"
printf 'n6:%s\n' "$v6"

Q='x y'
v7="$(printf '%s|%s' "${Q%% *}" "${Q#* }")"
printf 'n7:%s\n' "$v7"

v8="$(printf '%s' "${Q:+$(printf '%s' alt)}")"
printf 'n8:%s\n' "$v8"

# Mixed-part assembly: quoted + unquoted adjacency remains stable.
A='AB'
B='CD'
printf 'n9:%s\n' "x${A}""${B}""$(printf '%s' y)"
