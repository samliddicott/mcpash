#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - Parameter transformation operators ${v@Q}, ${v@P}, ${v@A}, ${v@a},
#   ${v@E}, ${v@U}, ${v@u}, ${v@L}

set +e
x='a b'

for op in Q P A a E U u L; do
  cmd="printf '%s' \"\${x@${op}}\""
  out="$(eval "$cmd" 2>&1)"
  rc=$?
  printf 'op:%s rc:%s out:%s\n' "$op" "$rc" "$out"
done
