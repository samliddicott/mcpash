#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - Parameter transform operators on positional and array expansions:
#   ${@@op}, ${*@op}, ${arr[@]@op}, ${arr[*]@op}

set +e
set -- 'a b' c
arr=('a b' c)

for op in Q P A a E U u L; do
  cmd_at="printf '<%s>' \"\${@@${op}}\""
  out_at="$(eval "$cmd_at" 2>&1)"
  rc_at=$?
  printf 'pos-at op:%s rc:%s out:%s\n' "$op" "$rc_at" "$out_at"

  cmd_star="printf '<%s>' \"\${*@${op}}\""
  out_star="$(eval "$cmd_star" 2>&1)"
  rc_star=$?
  printf 'pos-star op:%s rc:%s out:%s\n' "$op" "$rc_star" "$out_star"

  cmd_arr_at="printf '<%s>' \"\${arr[@]@${op}}\""
  out_arr_at="$(eval "$cmd_arr_at" 2>&1)"
  rc_arr_at=$?
  printf 'arr-at op:%s rc:%s out:%s\n' "$op" "$rc_arr_at" "$out_arr_at"

  cmd_arr_star="printf '<%s>' \"\${arr[*]@${op}}\""
  out_arr_star="$(eval "$cmd_arr_star" 2>&1)"
  rc_arr_star=$?
  printf 'arr-star op:%s rc:%s out:%s\n' "$op" "$rc_arr_star" "$out_arr_star"
done
