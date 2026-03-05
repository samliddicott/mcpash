#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: here-string redirection (<<<)

set +e

read -r hs <<< "hello_world"
printf 'hs:%s\n' "$hs"
