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

bash_cmd="bash --posix -i -c 'bind -l | sed -n 1,3p; bind -q self-insert >/dev/null 2>&1; echo bq:$?; complete -W \"one two\" mycmd; compopt -o nospace mycmd >/dev/null 2>&1; echo co:$?; compgen -A builtin ec >/dev/null 2>&1; echo cg:$?'"
mct_cmd="cd '$ROOT' && PYTHONPATH='$ROOT/src' MCTASH_MODE=bash python3 -m mctash -i -c 'bind -l | sed -n 1,3p; bind -q self-insert >/dev/null 2>&1; echo bq:$?; complete -W \"one two\" mycmd; compopt -o nospace mycmd >/dev/null 2>&1; echo co:$?; compgen -A builtin ec >/dev/null 2>&1; echo cg:$?'"

brc="$(run_pty bash "$bash_cmd")"
mrc="$(run_pty mctash "$mct_cmd")"

if [[ "$brc" -ne 0 || "$mrc" -ne 0 ]]; then
  echo "[FAIL] interactive command failed rc bash=$brc mctash=$mrc" >&2
  exit 1
fi

# Compare only stable marker lines; readline function lists vary across environments.
for marker in 'bq:0' 'co:0' 'cg:0'; do
  grep -Fq "$marker" "$tmpdir/bash.out" || { echo "[FAIL] bash missing marker $marker" >&2; exit 1; }
  grep -Fq "$marker" "$tmpdir/mctash.out" || { echo "[FAIL] mctash missing marker $marker" >&2; exit 1; }
done

echo "[PASS] completion interactive matrix"
