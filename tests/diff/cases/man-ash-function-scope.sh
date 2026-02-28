#!/usr/bin/env ash
# Coverage: function definition/invocation scope behavior.
# Areas:
# - function positional args shadow and restore caller positional args
# - local variables do not leak
# - return status from function body
set -eu

set -- outer1 outer2
f() {
  local X=inner
  printf 'f-args=%s:%s\n' "$1" "$2"
  set -- in1 in2
  printf 'f-set=%s:%s\n' "$1" "$2"
  return 7
}

set +e
f a b
st=$?
set -e

printf 'f-status=%s\n' "$st"
printf 'outer-args=%s:%s\n' "$1" "$2"
printf 'x-after=%s\n' "${X-unset}"
