#!/usr/bin/env ash
# Coverage: type option matrix behavior for this ash variant.
# Areas:
# - -t and -a behavior (supported vs treated as names)
# - status parity for missing names with options
set -eu

set +e
type -t cd >/dev/null 2>&1
st_t_cd=$?
type -a cd >/dev/null 2>&1
st_a_cd=$?
type -t definitely_missing >/dev/null 2>&1
st_t_missing=$?
type -a definitely_missing >/dev/null 2>&1
st_a_missing=$?
set -e

printf 'type-t-cd=%s\n' "$st_t_cd"
printf 'type-a-cd=%s\n' "$st_a_cd"
printf 'type-t-missing=%s\n' "$st_t_missing"
printf 'type-a-missing=%s\n' "$st_a_missing"
