#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 items 1..10 (row-level probe)

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"

if [[ -n "${BASH_VERSION-}" ]]; then
  self_shell_cmd='bash --posix'
else
  self_shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1) POSIXLY_CORRECT set in POSIX mode.
if [[ -n "${POSIXLY_CORRECT-}" ]]; then
  echo "JM:001:1"
else
  echo "JM:001:0"
fi

# 2) POSIX startup file ENV is used.
printf 'echo __ENV_HIT__\n' >"${tmp}/envrc"
chmod 700 "${tmp}/envrc"
out2="$(
  eval "ENV='${tmp}/envrc' HOME='${tmp}' ${self_shell_cmd} -i -c 'echo __CMD__'" 2>/dev/null | tr -d '\r'
)"
if [[ "$out2" == *"__ENV_HIT__"* && "$out2" == *"__CMD__"* ]]; then
  echo "JM:002:1"
else
  echo "JM:002:0"
fi

# 3) Alias expansion always enabled in non-interactive shells.
alias bp3='echo BP3'
echo "JM:003:$(bp3)"

# 4) Reserved words in reserved-word context do not alias-expand.
alias if='echo BAD_ALIAS_IF'
out4="$(if true; then echo OK; fi)"
echo "JM:004:${out4}"

# 5) Alias expansion in command substitution at parse time.
out5="$( { echo $(bp5); } 2>/dev/null )"
alias bp5='echo LATE'
if [[ -z "$out5" ]]; then
  echo "JM:005:empty"
else
  echo "JM:005:${out5}"
fi

# 6) `time` may be used as a simple command.
set +e
{ time; } >/dev/null 2>&1
st6=$?
set -e
echo "JM:006:${st6}"

# 7) Parser does not recognize `time` as reserved when next token starts '-'.
set +e
time -p >/dev/null 2>&1
st7=$?
set -e
echo "JM:007:${st7}"

# 8) In "${...}" under double quotes, single quotes are not special for
# closing brace quoting in POSIX mode.
unset bp8
out8="${bp8:-'}'}"
echo "JM:008:${out8}"

# 9) Redirection word does not do filename expansion in non-interactive mode.
(
  cd "${tmp}"
  : > a
  : > b
  f='*'
  : > $f
  [[ -e "*" ]] && echo "JM:009:1" || echo "JM:009:0"
)

# 10) Redirection word does not do word splitting.
(
  cd "${tmp}"
  f='a b'
  : > $f
  [[ -e "a b" ]] && echo "JM:010:1" || echo "JM:010:0"
)
