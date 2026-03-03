#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - operator expansion on arrays across unquoted/quoted [@]/[*] contexts
# - field-boundary behavior for replacement and trim operators
declare -a arr
arr=("ab x" "yyab" "abz")

printf 'u-repl:'
for x in ${arr[@]/ab/Q}; do printf '<%s>' "$x"; done
echo

printf 'q-at-repl:'
for x in "${arr[@]/ab/Q}"; do printf '<%s>' "$x"; done
echo

printf 'q-star-repl:'
for x in "${arr[*]/ab/Q}"; do printf '<%s>' "$x"; done
echo

printf 'u-trim:'
for x in ${arr[@]#ab}; do printf '<%s>' "$x"; done
echo

printf 'q-at-trim:'
for x in "${arr[@]#ab}"; do printf '<%s>' "$x"; done
echo

printf 'q-star-trim:'
for x in "${arr[*]#ab}"; do printf '<%s>' "$x"; done
echo
