#!/usr/bin/env ash
# Coverage: man ash read builtin.
# Areas:
# - IFS splitting and trailing-field behavior
# - backslash handling with and without -r
# - argument count behavior
# - unsupported option behavior for this ash variant
set -e

IFS=',' read first second <<'DATA1'
alpha,beta
DATA1
printf 'split=%s:%s\n' "$first" "$second"

read -r raw_line <<'DATA2'
line with \\backslash
DATA2
printf 'raw=%s\n' "$raw_line"

IFS=' ' read -r word1 word2 rest <<'DATA3'
one two three
DATA3
printf 'words=%s:%s:%s\n' "$word1" "$word2" "$rest"

# Without -r, backslash-newline is line continuation.
read cooked_line <<'DATA4'
left \
right
DATA4
printf 'cooked=%s\n' "$cooked_line"

# With no names, ash reports an argument-count error.
set +e
read 2>/dev/null <<'DATA5'
reply-value
DATA5
arg_status=$?
set -e
printf 'arg-status=%s\n' "$arg_status"

# Option matrix in this ash variant rejects -n/-d/-t with status 2.
set +e
read -n 1 onechar 2>/dev/null <<'DATA6'
x
DATA6
opt_status=$?
set -e
printf 'opt-status=%s\n' "$opt_status"
