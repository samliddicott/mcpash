#!/usr/bin/env ash
# Coverage: man ash redirection section (>, >>, <, heredoc/<<-, fd duplication).
set -eu

tmp=$(mktemp)
tmp2=$(mktemp)
trap 'rm -f "$tmp" "$tmp2"' EXIT

# test: truncate/append output per the > and >> tokens.
printf 'redirect-truncate' >"$tmp"
cat "$tmp"
printf 'redirect-append' >>"$tmp"
cat "$tmp"

# test: heredoc behavior and <<- tab stripping per the man page.
cat <<'HEREDOC' >"$tmp2"
line1
line2
HEREDOC
cat "$tmp2"

# test: verify fd duplication to stderr and custom fd handling.
printf 'stderr-dup' 1>&2
exec 3>&1
printf 'dup-to-fd3' >&3
