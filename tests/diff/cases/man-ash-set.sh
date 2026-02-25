#!/usr/bin/env ash
# Coverage: man ash 'set' builtin (option toggles, positional reset, listing behavior).
x=2
set -eu

# option toggles
set -o errexit
set -o noclobber
printf 'flags=%s\n' "$(printf '%s' "$-" | fold -w1 | sort | tr -d '\n')"

# positional parameter resets
set -- first second
printf 'args=%s:%s:%s\n' "$#" "$1" "$2"
set -- third
printf 'args2=%s:%s\n' "$#" "$1"
set --
printf 'args-zero=%s\n' "$#"

# listing the environment (per man page)
printf 'listing-start\n'
set | grep '^x='
printf 'listing-end\n'
