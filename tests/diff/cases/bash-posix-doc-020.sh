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
mkdir -p "$tmp/p1" "$tmp/p2"
printf '#!/usr/bin/env bash
echo P1
' >"$tmp/p1/c20"
printf '#!/usr/bin/env bash
echo P2
' >"$tmp/p2/c20"
chmod +x "$tmp/p1/c20" "$tmp/p2/c20"
PATH="$tmp/p1:$tmp/p2:/usr/bin:/bin"
hash -r
c20 >/dev/null 2>&1 || true
rm -f "$tmp/p1/c20"
out="$(c20 2>/dev/null || true)"
echo "JM:020:${out}"
