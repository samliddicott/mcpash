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

payload_file="$tmpdir/fc_interactive.input"
cat >"$payload_file" <<'INP'
set -o history
history -c
echo one >/dev/null
echo two
FCEDIT='sed -i s/echo\ two/echo\ TWO/'
fc -e "$FCEDIT" 'echo two' 'echo two'
fc -l -n -1 -1
exit
INP

bash_cmd="cat '$payload_file' | bash --posix -i"
mct_cmd="cd '$ROOT' && cat '$payload_file' | PYTHONPATH='$ROOT/src' MCTASH_MODE=bash python3 -m mctash -i"

brc="$(run_pty bash "$bash_cmd")"
mrc="$(run_pty mctash "$mct_cmd")"

if [[ "$brc" -ne 0 || "$mrc" -ne 0 ]]; then
  echo "[FAIL] fc interactive command failed rc bash=$brc mctash=$mrc" >&2
  exit 1
fi

for marker in 'echo TWO' 'TWO'; do
  grep -Fq "$marker" "$tmpdir/bash.out" || { echo "[FAIL] bash missing marker $marker" >&2; exit 1; }
  grep -Fq "$marker" "$tmpdir/mctash.out" || { echo "[FAIL] mctash missing marker $marker" >&2; exit 1; }
done

echo "[PASS] fc interactive matrix"
