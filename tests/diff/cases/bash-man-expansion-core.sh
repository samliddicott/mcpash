#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: tilde, command/backtick/arithmetic substitution, quote removal, command-subst newline trim

set +e

printf 'tilde:%s\n' ~
printf 'cmdsub:%s\n' "$(printf 'x\n')"
printf 'bq:%s\n' "`printf y`"
printf 'arith:%s\n' "$((1+2))"
printf 'quote-removal:%s\n' "a"'b'"c"
printf 'cmdtrim:%s\n' "$(printf 'q\n\n')"
