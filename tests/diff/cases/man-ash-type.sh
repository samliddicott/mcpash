#!/usr/bin/env ash
# Coverage: man ash `type` builtin.
# Areas:
# - function, alias, builtin, and external command reporting
# - aggregate status with missing names
set -eu
foo() { printf 'func-foo\n'; }
alias ll='ls -l'
norm_type() {
  type "$1" 2>/dev/null | sed 's/ is a shell function$/ is a function/'
}
foo
printf 'foo-type=%s\n' "$(norm_type foo)"
printf 'alias-type=%s\n' "$(norm_type ll)"
printf 'printf-type=%s\n' "$(norm_type printf)"
printf 'ls-type=%s\n' "$(norm_type ls)"
set +e
type cd echos >/dev/null 2>&1
status=$?
set -e
printf 'missing-status=%s\n' "$status"
printf 'cd-type=%s\n' "$(norm_type cd)"
