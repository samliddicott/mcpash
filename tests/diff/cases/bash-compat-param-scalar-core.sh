#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - scalar parameter default/alternate/assign/error operators
# - unset vs set-empty vs set-nonempty
# - length, prefix/suffix trims, substring, replacement
unset v || true
v_empty=""
v_set="abcabc"

echo "u-:${v-x}|u:-:${v:-x}|u+:${v+y}|u:+:${v:+y}"
echo "e-:${v_empty-x}|e:-:${v_empty:-x}|e+:${v_empty+y}|e:+:${v_empty:+y}"
echo "s-:${v_set-x}|s:-:${v_set:-x}|s+:${v_set+y}|s:+:${v_set:+y}"

unset a || true
echo "assign1:${a=foo}|a:$a"
a=""
echo "assign2:${a:=bar}|a:$a"

echo "len:${#v_set}"
echo "trim1:${v_set#a}|trim2:${v_set##a*}|trim3:${v_set%c}|trim4:${v_set%%c*}"
echo "substr1:${v_set:1}|substr2:${v_set:1:3}"
echo "repl1:${v_set/ab/XY}|repl2:${v_set//ab/XY}|repl3:${v_set/#ab/XY}|repl4:${v_set/%bc/ZZ}"
