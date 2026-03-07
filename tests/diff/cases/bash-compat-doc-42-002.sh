#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.42.002: single quotes in double-quoted ${...} word expansion.
ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${MCTASH_MODE-}" ]]; then
  runner_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
else
  runner_cmd="bash --posix"
fi
tmp_script="$(mktemp)"
tmp_err="$(mktemp)"
trap 'rm -f "$tmp_script" "$tmp_err"' EXIT
cat >"$tmp_script" <<'PAY'
v='abc}'
eval 'printf "%s\n" "${v%\'}\'}"'
PAY
set +e
out="$(eval "${runner_cmd} \"$tmp_script\"" 2>"$tmp_err")"; rc=$?
err_text="$(cat "$tmp_err")"
set -e
err=0
[ "$rc" -ne 0 ] && err=1
has_msg=0
[ -n "$out" ] && has_msg=1
has_err=0
[ -n "$err_text" ] && has_err=1
printf 'JM:BCOMPAT_42_002:err=%s has_msg=%s has_err=%s\n' "$err" "$has_msg" "$has_err"
