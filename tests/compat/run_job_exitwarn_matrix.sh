#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRICT="${STRICT:-0}"

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

run_case() {
  local label="$1"
  local cmd="$2"
  local input="$3"
  local out="$tmpdir/${label}.out"
  set +e
  script -qec "$cmd" /dev/null <"$input" | tr -d '\r' >"$out"
  local _rc=$?
  set -e
}

normalize() {
  local src="$1"
  local dst="$2"
  sed -E 's/\x1b\[[0-9;?]*[[:alpha:]]//g' "$src" \
    | awk '
      /^There are (running|stopped) jobs\.$/ { print "WARN"; next }
      /^JM:/ { print; next }
    ' >"$dst"
}

input_running="$tmpdir/running.in"
cat >"$input_running" <<'IN'
set -m
shopt -s checkjobs
sleep 2 &
exit
echo JM:after-running-first-exit
kill %1
wait %1 >/dev/null 2>&1
exit
IN

input_stopped="$tmpdir/stopped.in"
cat >"$input_stopped" <<'IN'
set -m
shopt -s checkjobs
sleep 5 &
kill -STOP $!
exit
echo JM:after-stopped-first-exit
kill -CONT %1
kill %1
wait %1 >/dev/null 2>&1
exit
IN

bash_cmd="bash --posix -i"
mct_cmd="cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i"

run_case "bash-running" "$bash_cmd" "$input_running"
run_case "mct-running" "$mct_cmd" "$input_running"
run_case "bash-stopped" "$bash_cmd" "$input_stopped"
run_case "mct-stopped" "$mct_cmd" "$input_stopped"

normalize "$tmpdir/bash-running.out" "$tmpdir/bash-running.norm"
normalize "$tmpdir/mct-running.out" "$tmpdir/mct-running.norm"
normalize "$tmpdir/bash-stopped.out" "$tmpdir/bash-stopped.norm"
normalize "$tmpdir/mct-stopped.out" "$tmpdir/mct-stopped.norm"

echo "=== job-exitwarn:running ==="
sed 's/^/  bash: /' "$tmpdir/bash-running.norm"
sed 's/^/  mct: /' "$tmpdir/mct-running.norm"

echo "=== job-exitwarn:stopped ==="
sed 's/^/  bash: /' "$tmpdir/bash-stopped.norm"
sed 's/^/  mct: /' "$tmpdir/mct-stopped.norm"

if [[ "$STRICT" == "1" ]]; then
  diff -u "$tmpdir/bash-running.norm" "$tmpdir/mct-running.norm" >/dev/null || {
    echo "[FAIL] exitwarn running mismatch" >&2
    exit 1
  }
  diff -u "$tmpdir/bash-stopped.norm" "$tmpdir/mct-stopped.norm" >/dev/null || {
    echo "[FAIL] exitwarn stopped mismatch" >&2
    exit 1
  }
fi

echo "[PASS] job exitwarn matrix"
