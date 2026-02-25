#!/usr/bin/env ash
# Coverage: man ash 'set' builtin (option toggles, -- positional reset, no-arg listing).
set -euo pipefail
x=2

# test: toggling options listed in the manual (errexit/noclobber/pipefail) and showing $-.
set -o errexit
set -o noclobber
set +o pipefail
printf 'flags=%s\n' "$-"

# test: 'set --' to reset positional parameters and check $# with/without args.
set -- first second
printf 'args=%s:%s:%s\n' "$#" "$1" "$2"
set -- third
printf 'args2=%s:%s\n' "$#" "$1"
set --
printf 'args-zero=%s\n' "$#"

# test: listing variables/environment (the manual says 'set' with no args prints them) so compare output.
printf 'listing-start\n'
set
printf 'listing-end\n'
