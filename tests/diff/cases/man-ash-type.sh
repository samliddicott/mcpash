#!/usr/bin/env ash
# Coverage: man ash `type` builtin (function, builtin, keyword, type -t output, and missing names).
set -euo pipefail
foo() { printf 'func-foo\n'; }
foo
printf 'foo-type=%s\n' "$(type foo)"
printf 'foo-type-t=%s\n' "$(type -t foo)"
printf 'printf-type-t=%s\n' "$(type -t printf)"
set +e
missing=$(type -t echos 2>/dev/null)
status=$?
set -e
printf 'missing-type-t=%s status=%s\n' "${missing}" "$status"
printf 'cd-type=%s\n' "$(type -a cd)"
