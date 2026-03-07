#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 21: non-executable PATH hits are not hashed.
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
printf 'echo hi\n' >"$tmpdir/c21"
chmod 0644 "$tmpdir/c21"
PATH="$tmpdir"
hash -r
set +e
cmdv="$(command -v c21 2>&1)"; rc_cmdv=$?
hash_line="$(hash 2>/dev/null | grep '/c21' || true)"
c21_out="$(c21 2>&1)"; rc_exec=$?
set -e
printf 'JM:021:cmdv=%s rc=%s\n' "$cmdv" "$rc_cmdv"
printf 'JM:021:hash=%s\n' "${hash_line:-<none>}"
printf 'JM:021:exec=%s rc=%s\n' "$c21_out" "$rc_exec"
