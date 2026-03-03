#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - assoc subscripts are string-key mode, not arithmetic-evaluated
# - numeric-like keys remain distinct strings
declare -A map
map[1+1]=expr
map[2]=two
map[01]=lead
echo "expr:${map[1+1]} two:${map[2]} lead:${map[01]}"
unset 'map[1+1]'
echo "after:${map[1+1]-unset} two:${map[2]} lead:${map[01]}"
