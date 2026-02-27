#!/usr/bin/env ash
# Coverage: man ash `type` builtin (function, builtin, keyword, type -t output, and missing names).
set -eu
foo() { printf 'func-foo\n'; }
foo
printf 'foo-type=%s\n' "$(type foo)"
printf 'printf-type=%s\n' "$(type printf)"
set +e
type echos >/dev/null 2>&1
status=$?
set -e
printf 'missing-status=%s\n' "$status"
printf 'cd-type=%s\n' "$(type cd)"
