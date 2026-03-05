#!/usr/bin/env ash
# Coverage: pathname expansion matrix for ordering, dotfiles, classes, slash segments, and noglob.
set -eu

d="/tmp/mctash-glob-full-$$"
mkdir -p "$d/sub"
: > "$d/a1.txt"
: > "$d/a2.txt"
: > "$d/b1.txt"
: > "$d/.hidden.txt"
: > "$d/sub/s1.log"
: > "$d/sub/s2.log"

# Basic class/range matching.
set -- "$d"/[ab][12].txt
printf 'gfm1:%s\n' "$#"

# Slash-segment matching.
set -- "$d"/sub/*.log
printf 'gfm2:%s\n' "$#"

# Dotfiles are not matched by * unless dot is explicit.
set -- "$d"/*
printf 'gfm3:%s\n' "$#"
set -- "$d"/.*.txt
printf 'gfm4:%s\n' "$#"

# Quoted glob stays literal.
set -- "$d/*.txt"
printf 'gfm5:%s:%s\n' "$#" "$(basename -- "$1")"

# No-match retains pattern literal.
set -- "$d"/nomatch-*.txt
printf 'gfm6:%s:%s\n' "$#" "$(basename -- "$1")"

# set -f disables glob expansion.
set -f
set -- "$d"/*.txt
printf 'gfm7:%s:%s\n' "$#" "$(basename -- "$1")"
set +f

rm -rf "$d"
