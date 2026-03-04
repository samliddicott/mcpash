#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): set/shift/export/readonly/unset/getopts

set +e
set -- alpha beta gamma
printf 'set-args:%s:%s:%s:%s\n' "$#" "$1" "$2" "$3"
shift
printf 'shift-1:%s:%s:%s\n' "$#" "$1" "$2"
shift 2
printf 'shift-3:%s\n' "$#"

XVAR='one two'
export XVAR
readonly RVAR=const
unset XVAR
# Run readonly-unset probe in a subshell so status is observable even on
# implementations where special-builtin errors terminate that shell context.
( unset RVAR ) 2>/dev/null
printf 'env:%s readonly-unset-rc:%s\n' "${XVAR-unset}" "$?"

set -- -a v1 -b v2
OPTIND=1
while getopts ':a:b:' opt; do
  case "$opt" in
    a) printf 'getopts:a:%s\n' "$OPTARG" ;;
    b) printf 'getopts:b:%s\n' "$OPTARG" ;;
    :) printf 'getopts:missing:%s\n' "$OPTARG" ;;
    \?) printf 'getopts:bad:%s\n' "$OPTARG" ;;
  esac
done
printf 'getopts:end:%s\n' "$OPTIND"
