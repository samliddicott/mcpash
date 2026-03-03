#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - assignment-word expansion for special/positional parameters
# - plain and braced forms in assignment context
# - default/alternate forms for positional parameters

set -- "a b" c
x=$@
y=$*
z=$1
w=${1:-d}
u=${9:-d}
v=${2:+Y}
q=${9:+Y}
r=${#1}

printf 'x=<%s>\n' "$x"
printf 'y=<%s>\n' "$y"
printf 'z=<%s>\n' "$z"
printf 'w=<%s>\n' "$w"
printf 'u=<%s>\n' "$u"
printf 'v=<%s>\n' "$v"
printf 'q=<%s>\n' "$q"
printf 'r=<%s>\n' "$r"

set --
empty_at=$@
empty_star=$*
printf 'ea=<%s>\n' "$empty_at"
printf 'es=<%s>\n' "$empty_star"
