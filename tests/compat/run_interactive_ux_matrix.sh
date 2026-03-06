#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

run_pty() {
  local label="$1"
  local cmd="$2"
  local out="$tmpdir/${label}.out"
  set +e
  script -qec "$cmd" /dev/null | tr -d '\r' >"$out"
  local rc=$?
  set -e
  echo "$rc"
}

input_payload="$(cat <<'EOF'
PROMPT_COMMAND="echo PCMD"
history -s "echo HISTMARK"
!!
debian_chroot="dch"
PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
echo PROMPTVARS_ON
shopt -u promptvars
PS1='${debian_chroot:+($debian_chroot)}\$ '
echo PROMPTVARS_OFF
shopt -s promptvars
PS1='X\uY\wZ\$ '
exit
EOF
)"
payload_file="$tmpdir/interactive_ux.input"
printf '%s\n' "$input_payload" >"$payload_file"

bash_cmd="cat '$payload_file' | bash --posix -i"
mct_cmd="cd '$ROOT' && cat '$payload_file' | PYTHONPATH='$ROOT/src' MCTASH_MODE=bash python3 -m mctash -i"

brc="$(run_pty bash "$bash_cmd")"
mrc="$(run_pty mctash "$mct_cmd")"

if [[ "$brc" -ne 0 || "$mrc" -ne 0 ]]; then
  echo "[FAIL] interactive UX command failed rc bash=$brc mctash=$mrc" >&2
  exit 1
fi

for marker in 'PCMD' 'HISTMARK' 'echo HISTMARK'; do
  grep -Fq "$marker" "$tmpdir/bash.out" || { echo "[FAIL] bash missing marker $marker" >&2; exit 1; }
  grep -Fq "$marker" "$tmpdir/mctash.out" || { echo "[FAIL] mctash missing marker $marker" >&2; exit 1; }
done

# Prompt variable expansion marker: debian_chroot interpolation appears when
# promptvars is enabled.
for shell_out in "$tmpdir/bash.out" "$tmpdir/mctash.out"; do
  grep -Eq '\(dch\).*@.*:.*[#$] ' "$shell_out" || {
    echo "[FAIL] missing promptvars-on interpolation marker in $shell_out" >&2
    exit 1
  }
done

# Prompt expansion lane marker: PS1 with \u \w \$ should produce prompt line containing X..Y..Z..
grep -Eq 'X.*Y.*Z[#$] ' "$tmpdir/mctash.out" || {
  echo "[FAIL] mctash missing expanded PS1 marker" >&2
  exit 1
}

echo "[PASS] interactive UX matrix"
