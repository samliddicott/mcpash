#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: fc editor selection surface in ash-advertised mode.
# NOTE: temporary comparator override to bash because current ash comparator lacks `fc`.
# Areas:
# - FCEDIT precedence
# - EDITOR fallback
# - -e flag override
# - editor subprocess gets shell runtime env snapshot
set +e
set -o history
echo one >/dev/null
echo two >/dev/null

FCEDIT=true EDITOR=false fc 'echo one' 'echo one' >/dev/null 2>&1
s_fcedit=$?

unset FCEDIT
EDITOR=true fc 'echo two' 'echo two' >/dev/null 2>&1
s_editor=$?

FCEDIT=false EDITOR=false fc -e true 'echo two' 'echo two' >/dev/null 2>&1
s_flag=$?

tmpd="$(mktemp -d)"
trap '/bin/rm -rf "$tmpd"' EXIT
cat >"$tmpd/editor" <<'SH'
#!/usr/bin/env sh
printf '%s\n' "$FC_ENV_PROBE" >"$1.env"
exit 0
SH
chmod +x "$tmpd/editor"
export FC_ENV_PROBE="fc-env-ok"
fc -e "$tmpd/editor" 'echo two' 'echo two' >/dev/null 2>&1
s_env=$?
probe_out="$(cat "$tmpd"/*.env 2>/dev/null || true)"

printf 'fc-editor=%s,%s,%s,%s,%s\n' "$s_fcedit" "$s_editor" "$s_flag" "$s_env" "$probe_out"
