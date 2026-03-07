#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.50.003: here-string/here-doc fd backing probe (pipe vs temp file path).
set +e
hs="$(readlink /proc/$$/fd/0 <<<"x" 2>/dev/null)"; rc_hs=$?
hd="$(readlink /proc/$$/fd/0 <<'HD' 2>/dev/null
x
HD
)"; rc_hd=$?
set -e
printf 'JM:BCOMPAT_50_003:hs=%s(%s) hd=%s(%s)\n' "$hs" "$rc_hs" "$hd" "$rc_hd"
