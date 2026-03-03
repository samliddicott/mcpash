#!/usr/bin/env bash
# DIFF_BASELINE: bash

declare -A map
map[a]=1
map[b]=2
echo "n:${#map[@]}"
echo "keys:${!map[@]}"
