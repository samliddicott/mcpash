#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): break/continue semantics.

set +e
acc=""
for i in 1 2; do
  for j in a b; do
    if [ "$i$j" = "1a" ]; then
      continue 2
    fi
    acc="${acc}${i}${j},"
  done
done
printf 'continue2:%s\n' "$acc"

acc2=""
for i in 1 2; do
  for j in a b; do
    acc2="${acc2}${i}${j},"
    break 2
  done
done
printf 'break2:%s\n' "$acc2"
