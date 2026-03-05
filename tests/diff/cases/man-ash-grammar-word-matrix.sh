#!/usr/bin/env ash
# Coverage: parser/word grammar boundaries (continuations, reserved words, nested compounds).
set -eu

# Backslash-newline joins logical line in simple list.
val=$(
  echo A\
B
)
printf 'gwm1:%s\n' "$val"

# Reserved words as literals in argument position.
printf 'gwm2:%s\n' "if" "then" "fi"

# Nested compound/list shape should parse and execute deterministically.
if { :; } && ( : ); then
  printf 'gwm3:ok\n'
else
  printf 'gwm3:bad\n'
fi

# Case grammar with alternation and optional final terminator.
case x in
  a|b) printf 'gwm4:no\n' ;;
  x) printf 'gwm4:yes\n' ;;
esac

# Word concatenation across quote boundaries.
printf 'gwm5:%s\n' "a"'b'"c"

# Command substitution in quoted context with nested substitution.
v="$(printf '%s' "$(printf '%s' q)")"
printf 'gwm6:%s\n' "$v"
