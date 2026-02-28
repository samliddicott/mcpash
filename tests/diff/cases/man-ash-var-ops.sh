#!/usr/bin/env ash
# Coverage: braced parameter operator matrix.
# Areas:
# - default/assign/alternate/error operators
# - prefix/suffix pattern removal variants
set -eu

unset U || true
echo d1:${U:-def}
echo a1:${U:=setv}
echo u1:$U
echo p1:${U:+alt}

U=
echo d2:${U:-def2}
echo p2:${U:+alt2}

S=abcabc
echo h1:${S#*b}
echo h2:${S##*b}
echo t1:${S%b*}
echo t2:${S%%b*}
