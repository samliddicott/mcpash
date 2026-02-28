#!/usr/bin/env ash
# Coverage: pathname expansion ordering/no-match/quote interactions.
set -eu

d="/tmp/mctash-glob-$$"
mkdir -p "$d"
: > "$d/a1.txt"
: > "$d/a2.txt"
: > "$d/b.txt"

set -- "$d"/a*.txt
printf 'g1=%s\n' "$#"

# quoted glob must not expand
set -- "$d/a*.txt"
printf 'g2=%s\n' "$#"
printf 'g2v=%s\n' "$(basename -- "$1")"

# no-match behavior should preserve pattern literal in this ash
set -- "$d"/z*.txt
printf 'g3=%s\n' "$#"
printf 'g3v=%s\n' "$(basename -- "$1")"

rm -rf "$d"
