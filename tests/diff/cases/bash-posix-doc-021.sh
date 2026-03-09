#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 21: non-executable PATH hits are not hashed.
tmpdir="$(mktemp -d)"
trap '/bin/rm -rf "$tmpdir"' EXIT
printf 'echo hi\n' >"$tmpdir/c21"
chmod 0644 "$tmpdir/c21"
PATH="$tmpdir"
hash -r
set +e
cmdv="$(command -v c21 2>&1)"; rc_cmdv=$?
hash_line="$(hash 2>/dev/null || true)"
hash_has=0
case "$hash_line" in
  *"/c21"*) hash_has=1 ;;
esac
c21_out="$(c21 2>&1)"; rc_exec=$?
set -e
perm=0
case "$c21_out" in
  *[Pp]ermission\ denied*) perm=1 ;;
esac
printf 'JM:021:cmdv=%s rc=%s\n' "$cmdv" "$rc_cmdv"
printf 'JM:021:hash_has=%s\n' "$hash_has"
printf 'JM:021:exec_rc=%s perm=%s\n' "$rc_exec" "$perm"
