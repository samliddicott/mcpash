#!/usr/bin/env ash
# Coverage: extended braced-parameter operator matrix (ash/POSIX in-scope).
# Areas:
# - unset/null/set behavior for -, :-, +, :+, =, :=, ?, :?
# - quoted/unquoted operator-word handling
# - shortest/longest prefix/suffix removal with glob patterns
# - positional parameter behavior for default operators

set -eu

unset U || true
N=''
S='alpha-beta-gamma'

# Default / alternate / assign matrix.
printf 'm1:%s\n' "${U-word}"
printf 'm2:%s\n' "${U:-word}"
printf 'm3:%s\n' "${N-word}"
printf 'm4:%s\n' "${N:-word}"

printf 'm5:%s\n' "${U+alt}"
printf 'm6:%s\n' "${U:+alt}"
printf 'm7:%s\n' "${N+alt}"
printf 'm8:%s\n' "${N:+alt}"

printf 'm9:%s\n' "${U=ass}"
printf 'm10:%s\n' "$U"
unset U || true
printf 'm11:%s\n' "${U:=ass2}"
printf 'm12:%s\n' "$U"

# Pattern removals.
printf 'm13:%s\n' "${S#*-}"
printf 'm14:%s\n' "${S##*-}"
printf 'm15:%s\n' "${S%-*}"
printf 'm16:%s\n' "${S%%-*}"

# Quoted operator words.
unset Q || true
printf 'm17:%s\n' "${Q:-x y z}"
Q=''
printf 'm18:%s\n' "${Q:-x y z}"
Q='ok'
printf 'm19:%s\n' "${Q:+x y z}"

# Positional parameters with default operators.
set -- p1 '' p3
printf 'm20:%s\n' "${1:-d1}"
printf 'm21:%s\n' "${2:-d2}"
printf 'm22:%s\n' "${3:-d3}"
printf 'm23:%s\n' "${4:-d4}"
