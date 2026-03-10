#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.50.003: here-string/here-doc fd backing probe (pipe vs temp file path).
set +e
readlink /proc/$$/fd/0 <<<"x" >/tmp/bcompat50_003_hs 2>/dev/null; rc_hs=$?
readlink /proc/$$/fd/0 <<'HD' >/tmp/bcompat50_003_hd 2>/dev/null
x
HD
rc_hd=$?
set -e
hs="$(cat /tmp/bcompat50_003_hs 2>/dev/null || true)"
hd="$(cat /tmp/bcompat50_003_hd 2>/dev/null || true)"
rm -f /tmp/bcompat50_003_hs /tmp/bcompat50_003_hd
if [ -n "$hs" ]; then hs_nonempty=1; else hs_nonempty=0; fi
if [ -n "$hd" ]; then hd_nonempty=1; else hd_nonempty=0; fi
printf 'JM:BCOMPAT_50_003:hs_rc=%s hd_rc=%s hs_nonempty=%s hd_nonempty=%s\n' "$rc_hs" "$rc_hd" "$hs_nonempty" "$hd_nonempty"
