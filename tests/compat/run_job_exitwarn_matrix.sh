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
      /^JM:pid:[0-9]+$/ { print "JM:pid"; next }
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

input_second="$tmpdir/second-exit.in"
cat >"$input_second" <<'IN'
set -m
shopt -s checkjobs
sleep 20 &
pid=$!
echo JM:pid:$pid
kill -STOP $pid
exit
exit
IN

bash_cmd="bash --posix -i"
mct_cmd="cd '$ROOT' && MCTASH_DIAG_STYLE=bash PYTHONPATH='$ROOT/src' python3 -m mctash --posix -i"

run_case "bash-running" "$bash_cmd" "$input_running"
run_case "mct-running" "$mct_cmd" "$input_running"
run_case "bash-stopped" "$bash_cmd" "$input_stopped"
run_case "mct-stopped" "$mct_cmd" "$input_stopped"
run_case "bash-second" "$bash_cmd" "$input_second"
run_case "mct-second" "$mct_cmd" "$input_second"

normalize "$tmpdir/bash-running.out" "$tmpdir/bash-running.norm"
normalize "$tmpdir/mct-running.out" "$tmpdir/mct-running.norm"
normalize "$tmpdir/bash-stopped.out" "$tmpdir/bash-stopped.norm"
normalize "$tmpdir/mct-stopped.out" "$tmpdir/mct-stopped.norm"
normalize "$tmpdir/bash-second.out" "$tmpdir/bash-second.norm"
normalize "$tmpdir/mct-second.out" "$tmpdir/mct-second.norm"

echo "=== job-exitwarn:running ==="
sed 's/^/  bash: /' "$tmpdir/bash-running.norm"
sed 's/^/  mct: /' "$tmpdir/mct-running.norm"

echo "=== job-exitwarn:stopped ==="
sed 's/^/  bash: /' "$tmpdir/bash-stopped.norm"
sed 's/^/  mct: /' "$tmpdir/mct-stopped.norm"

echo "=== job-exitwarn:second-exit ==="
sed 's/^/  bash: /' "$tmpdir/bash-second.norm"
sed 's/^/  mct: /' "$tmpdir/mct-second.norm"

bash_pid="$(rg -o 'JM:pid:[0-9]+' "$tmpdir/bash-second.out" | tail -n1 | cut -d: -f3)"
mct_pid="$(rg -o 'JM:pid:[0-9]+' "$tmpdir/mct-second.out" | tail -n1 | cut -d: -f3)"
bash_alive=0
mct_alive=0
if [[ -n "${bash_pid:-}" ]] && kill -0 "$bash_pid" 2>/dev/null; then
  bash_alive=1
fi
if [[ -n "${mct_pid:-}" ]] && kill -0 "$mct_pid" 2>/dev/null; then
  mct_alive=1
fi
echo "  bash: JM:pid_alive:$bash_alive"
echo "  mct: JM:pid_alive:$mct_alive"

if [[ "$STRICT" == "1" ]]; then
  diff -u "$tmpdir/bash-running.norm" "$tmpdir/mct-running.norm" >/dev/null || {
    echo "[FAIL] exitwarn running mismatch" >&2
    exit 1
  }
  diff -u "$tmpdir/bash-stopped.norm" "$tmpdir/mct-stopped.norm" >/dev/null || {
    echo "[FAIL] exitwarn stopped mismatch" >&2
    exit 1
  }
  diff -u "$tmpdir/bash-second.norm" "$tmpdir/mct-second.norm" >/dev/null || {
    echo "[FAIL] exitwarn second-exit marker mismatch" >&2
    exit 1
  }
  if [[ "$bash_alive" -ne "$mct_alive" ]]; then
    echo "[FAIL] exitwarn second-exit pid liveness mismatch" >&2
    exit 1
  fi
  if [[ "$mct_alive" -ne 0 ]]; then
    echo "[FAIL] exitwarn second-exit left stopped job alive" >&2
    exit 1
  fi
fi

echo "[PASS] job exitwarn matrix"
