ROOT="${ROOT:-.}"

. "$ROOT/scripts/ash-core-stubs.sh"
. "$ROOT/external/ash-shell-test/lib/util.sh"
. "$ROOT/external/ash-shell-test/callable.sh"

Test__callable_main "$ROOT/tests/ash-demo"
