#!/usr/bin/env ash
# Coverage: man ash 'getopts' builtin (option parsing, missing arguments, error handling, OPTIND behavior).
set -e

# test: iterate options that take args and flags, check OPTARG and OPTIND.
set -- -a alpha -b -c
optstring="a:bc"
OPTIND=1
while getopts "$optstring" opt; do
  printf 'opt=%s optarg=%s optind=%s\n' "$opt" "${OPTARG-}" "$OPTIND"
  case "$opt" in
    a)
      ;;
    b)
      ;;
    c)
      ;;
    ?)
      printf 'error=%s\n' "$OPTARG"
      ;;
  esac
done
printf 'after-loop-OPTIND=%s\n' "$OPTIND"

# test: missing argument handling when colon-prefix is present in optstring.
set -- -a
optstring=":a"
OPTIND=1
if ! getopts "$optstring" opt_missing; then
  printf 'missing-status=%s OPTARG=%s OPTIND=%s\n' "$?" "${OPTARG-}" "$OPTIND"
fi
