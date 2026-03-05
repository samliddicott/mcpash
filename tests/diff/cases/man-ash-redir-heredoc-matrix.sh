#!/usr/bin/env ash
# Coverage: redirection/here-doc matrix (ordering, quoted delimiter, <<-, fd close/dup).
set -eu

d="/tmp/mctash-redir-matrix-$$"
mkdir -p "$d"
out="$d/out.txt"
err="$d/err.txt"

touch "$out" "$err"

# Ordering is observable: 2>&1 >out keeps stderr on original stderr.
{
  sh -c 'echo so; echo se 1>&2' 2>&1 >"$out"
} 2>"$err"
printf 'rhm1:%s:%s\n' "$(wc -l <"$out")" "$(wc -l <"$err")"

# Inverse ordering sends both streams to out.
: >"$out"
: >"$err"
{
  sh -c 'echo so; echo se 1>&2' >"$out" 2>&1
} 2>"$err"
printf 'rhm2:%s:%s\n' "$(wc -l <"$out")" "$(wc -l <"$err")"

# Quoted delimiter disables expansion.
X='abc def'
cat <<'QEOF' >"$out"
$X
QEOF
printf 'rhm3:%s\n' "$(cat "$out")"

# <<- strips leading tabs in body.
cat <<-TEOF >"$out"
	line1
	$X
TEOF
# Collapse to one line for stable compare.
printf 'rhm4:%s\n' "$(tr '\n' '|' <"$out")"

# Multiple here-docs in one simple command preserve left-to-right attachment.
cat <<A <<B >"$out"
one
A
two
B
printf 'rhm5:%s\n' "$(tr '\n' '|' <"$out")"

# FD close behavior.
: >"$out"
if sh -c 'echo x >&9' 9>&- >"$out" 2>/dev/null; then
  printf 'rhm6:ok\n'
else
  printf 'rhm6:fail\n'
fi

rm -rf "$d"
