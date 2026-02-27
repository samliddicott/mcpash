#!/usr/bin/env ash
# Coverage: man ash `type` builtin.
# Areas:
# - function, alias, builtin, and external command reporting
# - aggregate status with missing names
set -eu
foo() { printf 'func-foo\n'; }
alias ll='ls -l'
foo
printf 'foo-type=%s\n' "$(type foo)"
printf 'alias-type=%s\n' "$(type ll)"
printf 'printf-type=%s\n' "$(type printf)"
printf 'ls-type=%s\n' "$(type ls)"
set +e
type cd echos >/dev/null 2>&1
status=$?
set -e
printf 'missing-status=%s\n' "$status"
printf 'cd-type=%s\n' "$(type cd)"
