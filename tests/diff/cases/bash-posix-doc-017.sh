#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
if [[ -n "${BASH_VERSION-}" ]]; then
  self_shell_cmd='bash --posix'
else
  self_shell_cmd="PYTHONPATH='${ROOT_DIR}/src' python3 -m mctash --posix"
fi

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/hbin"
printf '#!/usr/bin/env bash
echo HIT17
' >"$tmp/hbin/c17"
chmod +x "$tmp/hbin/c17"
PATH="~/hbin:/usr/bin:/bin"
set +e
c17 >/dev/null 2>&1
st=$?
set -e
echo "JM:017:${st}"
