#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: declare/typeset/local parity lane (non-interactive).
# Areas:
# - typeset alias to declare
# - local scoping and outside-function failure
# - declare integer attribute coercion
set +e

f() {
  local lx=1
  typeset ty=2
  declare -i nn=07
  echo "f:${lx}:${ty}:${nn}"
}

f
s_f=$?
local q=9 >/dev/null 2>&1
s_local_outside=$?

declare -i gi=7
printf 'g:%s\n' "$gi"
typeset -p gi >/dev/null 2>&1
s_typeset_p=$?

printf 'st:%s,%s,%s\n' "$s_f" "$s_local_outside" "$s_typeset_p"
