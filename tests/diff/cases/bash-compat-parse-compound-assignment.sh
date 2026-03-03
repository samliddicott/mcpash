#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - compound assignment lexeme preservation through parser/LST->ASDL mapping
# - escaped-space and line-continuation element shapes
declare -a arr
arr=(a\
b "c d" e\ f)
echo "n:${#arr[@]} 0:<${arr[0]}> 1:<${arr[1]}> 2:<${arr[2]}>"

arr=( "x y" z\ w )
echo "m:${#arr[@]} 0:<${arr[0]}> 1:<${arr[1]}>"
