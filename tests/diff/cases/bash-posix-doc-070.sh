#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 70: command/type treatment of non-executable PATH entries.
tmpdir="$(mktemp -d)"
trap '/bin/rm -rf "$tmpdir"' EXIT
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
cv_found=0
[ -n "$cv" ] && cv_found=1
ty_found=0
case "$ty" in
  *not\ found*) ty_found=0 ;;
  *) ty_found=1 ;;
esac
perm=0
case "$out_exec" in
  *[Pp]ermission\ denied*) perm=1 ;;
esac
printf 'JM:070:cv_rc=%s cv_found=%s\n' "$rc_cv" "$cv_found"
printf 'JM:070:type_rc=%s type_found=%s\n' "$rc_ty" "$ty_found"
printf 'JM:070:exec_rc=%s perm=%s\n' "$rc_exec" "$perm"
