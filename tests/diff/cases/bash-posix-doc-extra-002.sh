#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Extra 2: with FCEDIT unset, fc should use EDITOR.
set -o history
echo fce2a >/dev/null
echo fce2b >/dev/null
tmpd="$(mktemp -d)"
tmp_out="$(mktemp)"
tmp_err="$(mktemp)"
trap '/bin/rm -rf "$tmpd"; /bin/rm -f "$tmp_out" "$tmp_err"' EXIT
cat >"$tmpd/editor" <<SH
#!/usr/bin/env sh
echo editor >"$tmpd/mark"
exit 0
SH
chmod +x "$tmpd/editor"
set +e
unset FCEDIT
EDITOR="$tmpd/editor" fc 'echo fce2a >/dev/null' 'echo fce2a >/dev/null' >"$tmp_out" 2>"$tmp_err"
rc=$?
set -e
used_editor=0
[ -f "$tmpd/mark" ] && used_editor=1
printf 'JM:EXTRA002:rc=%s used_editor=%s\n' "$rc" "$used_editor"
