#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 47: alias display formatting without -p
unalias zz47 2>/dev/null || true
alias zz47='echo z'
a=$(alias zz47)
b=$(alias -p zz47)
case "$a" in
  alias\ *) echo JM:047:a_alias ;; 
  *) echo JM:047:a_plain ;;
esac
case "$b" in
  alias\ *) echo JM:047:b_alias ;;
  *) echo JM:047:b_plain ;;
esac

