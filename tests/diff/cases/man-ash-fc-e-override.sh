#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: explicit -e editor overrides FCEDIT/EDITOR.
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
set +e
set -o history
history -c

echo one >/dev/null
echo two >/dev/null

tmpd="$(mktemp -d)"
trap '/bin/rm -rf "$tmpd"' EXIT
cat >"$tmpd/fcedit" <<'SH'
#!/usr/bin/env sh
echo fcedit >"$1.which"
exit 0
SH
cat >"$tmpd/override" <<'SH'
#!/usr/bin/env sh
echo override >"$1.which"
exit 0
SH
chmod +x "$tmpd/fcedit" "$tmpd/override"

FCEDIT="$tmpd/fcedit" EDITOR="$tmpd/fcedit" fc -e "$tmpd/override" 'echo two' 'echo two' >/dev/null 2>&1
s_override=$?
which_editor="$(cat "$tmpd"/*.which 2>/dev/null || true)"

printf 'fc-e-override=%s,%s\n' "$s_override" "$which_editor"
