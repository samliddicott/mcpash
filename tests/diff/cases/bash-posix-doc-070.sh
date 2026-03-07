#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 70: command/type treatment of non-executable PATH entries.
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
cat >"$tmpdir/t70" <<'SH'
echo hi-from-t70
SH
chmod 0644 "$tmpdir/t70"
PATH="$tmpdir"
set +e
cv="$(command -v t70 2>&1)"; rc_cv=$?
ty="$(type t70 2>&1)"; rc_ty=$?
out_exec="$(t70 2>&1)"; rc_exec=$?
set -e
printf 'JM:070:cv:%s rc=%s\n' "$cv" "$rc_cv"
printf 'JM:070:type:%s rc=%s\n' "$ty" "$rc_ty"
printf 'JM:070:exec:%s rc=%s\n' "$out_exec" "$rc_exec"
