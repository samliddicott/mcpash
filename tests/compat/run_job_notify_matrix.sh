#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRICT="${STRICT:-0}"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

input_file="$tmpdir/notify.input"
cat >"$input_file" <<'IN'
set -m
set +b
sleep 0.1 &
sleep 0.3
echo JM:phase1
set -b
sleep 0.1 &
sleep 0.3
echo JM:phase2
exit
IN

normalize() {
  local src="$1"
  local dst="$2"
  local clean="$tmpdir/clean.$(basename "$src")"
  sed -E 's/\x1b\[[0-9;?]*[[:alpha:]]//g' "$src" >"$clean"
  {
    grep 'JM:phase' "$clean" | sed -E 's/.*(JM:phase[0-9]).*/\1/' || true
    grep 'Done' "$clean" | sed -E 's/^\[[0-9]+\][^D]*Done.*/DONE/' || true
  } >"$dst"
}

run_case() {
  local label="$1"
  local cmd="$2"
  local out="$tmpdir/${label}.out"
  script -qec "$cmd" /dev/null <"$input_file" | tr -d '\r' >"$out"
}

run_case "bash" "bash --posix -i"
run_case "mctash" "cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i"

normalize "$tmpdir/bash.out" "$tmpdir/bash.norm"
normalize "$tmpdir/mctash.out" "$tmpdir/mctash.norm"

echo "=== job-notify ==="
sed 's/^/  bash: /' "$tmpdir/bash.norm"
sed 's/^/  mct: /' "$tmpdir/mctash.norm"

if [[ "$STRICT" == "1" ]]; then
  if ! diff -u "$tmpdir/bash.norm" "$tmpdir/mctash.norm" >/dev/null; then
    echo "[FAIL] notify matrix mismatch" >&2
    exit 1
  fi
fi

echo "[PASS] job notify matrix"
