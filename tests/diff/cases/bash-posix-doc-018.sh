#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${MCTASH_MODE-}" ]]; then
  runner_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  runner_cmd='bash --posix'
fi

tmp_out="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_out" "$tmp_err"' EXIT
set +e
eval "${runner_cmd} -c 'eval \"export(){ :; }\" >/dev/null 2>&1'" >"$tmp_out" 2>"$tmp_err"
rc_def=$?
type_out="$(eval "${runner_cmd} -c 'type export 2>&1'" 2>/dev/null)"
set -e
def_err=0
[ "$rc_def" -ne 0 ] && def_err=1
is_function=0
case "$type_out" in
  *function*) is_function=1 ;;
esac
is_builtin=0
case "$type_out" in
  *builtin*) is_builtin=1 ;;
esac
printf 'JM:018:def_err=%s function=%s builtin=%s\n' "$def_err" "$is_function" "$is_builtin"
