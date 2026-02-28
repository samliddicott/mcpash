#!/usr/bin/env ash
# Coverage: heredoc edge semantics (quoted delimiters, <<-, multiple heredocs).
set -eu

X=abc
cat <<EOF1
$X
EOF1

cat <<'EOF2'
$X
EOF2

cat <<-EOF3
	line1
	$X
EOF3

cat <<A <<B
one
A
two
B
