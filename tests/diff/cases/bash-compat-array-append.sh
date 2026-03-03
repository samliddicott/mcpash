#!/usr/bin/env bash
# DIFF_BASELINE: bash

declare -a arr
arr=(a b)
arr+=(c d)
echo "vals:${arr[@]} n:${#arr[@]}"
