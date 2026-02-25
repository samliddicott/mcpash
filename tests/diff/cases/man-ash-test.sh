#!/usr/bin/env ash
# Coverage: man ash '[ test ]' and 'test' builtins (file checks, string/numeric comparisons, logical combos, negation).
set -eu

# test: existence and type tests from the builtin section.
if test -e "${0}"; then printf 'exists\n'; fi
if test -f /dev/null; then printf 'dev-null\n'; fi
if test -d /; then printf 'root-dir\n'; fi

# test: string equality/inequality coverage as described in the strings subsection.
if [ foo = foo ]; then printf 'string-eq\n'; fi
if [ foo != bar ]; then printf 'string-ne\n'; fi

# test: numeric comparisons and arithmetic expansion coverage described in the arithmetic section.
if [ 3 -gt 2 ]; then printf 'numeric-gt\n'; fi
if test 5 -eq $((2 + 3)); then printf 'numeric-eq\n'; fi

# test: combined logical operators and negation coverage.
if test -n foo && test foo != bar; then printf 'and-combo\n'; fi
if ! test -n ""; then printf 'negated-empty\n'; fi
