#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: bash redirection extensions (&>, &>>, {varname}>...)

set +e

tmp="${TMPDIR:-/tmp}/mctash-redir-ext-$$"
: > "$tmp"

echo both &> "$tmp"
cat "$tmp"

echo append1 &>> "$tmp"
cat "$tmp"

exec {fd}>"$tmp"
echo named-fd >&"$fd"
exec {fd}>&-
cat "$tmp"

rm -f "$tmp"
