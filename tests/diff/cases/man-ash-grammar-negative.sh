#!/usr/bin/env ash
# Coverage: grammar rejection paths via eval (status-based).
# Areas:
# - malformed nested compounds
# - separator/operator mismatch
# - unterminated constructs
set -eu

set +e

( eval 'if true; then echo ok; else' >/dev/null 2>&1 )
echo bad-if-missing-fi=$?

( eval 'while true; do echo x' >/dev/null 2>&1 )
echo bad-while-missing-done=$?

( eval '{ echo a; ' >/dev/null 2>&1 )
echo bad-group-missing-brace=$?

( eval 'for i in a b do echo $i; done' >/dev/null 2>&1 )
echo bad-for-missing-semi=$?

( eval 'echo a && || echo b' >/dev/null 2>&1 )
echo bad-andor-op=$?

( eval '( echo a' >/dev/null 2>&1 )
echo bad-subshell-close=$?

set -e
