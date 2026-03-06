#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

bash_out="$tmpdir/bash.out"
mct_out="$tmpdir/mctash.out"

set +e
timeout 6s script -qec 'TMOUT=1 bash --posix -i' /dev/null >"$bash_out" 2>&1
bash_rc=$?
timeout 6s script -qec "cd '$ROOT' && TMOUT=1 PYTHONPATH='$ROOT/src' MCTASH_MODE=bash python3 -m mctash -i" /dev/null >"$mct_out" 2>&1
mct_rc=$?
set -e

if [[ "$bash_rc" -ne 0 ]]; then
  echo "[FAIL] bash TMOUT baseline did not exit cleanly (rc=$bash_rc)" >&2
  tail -n 40 "$bash_out" >&2 || true
  exit 1
fi

if [[ "$mct_rc" -eq 124 ]]; then
  echo "[FAIL] mctash TMOUT probe timed out (shell did not auto-logout)" >&2
  tail -n 40 "$mct_out" >&2 || true
  exit 1
fi

if [[ "$mct_rc" -ne 0 ]]; then
  echo "[FAIL] mctash TMOUT probe exited with rc=$mct_rc" >&2
  tail -n 40 "$mct_out" >&2 || true
  exit 1
fi

echo "[PASS] interactive TMOUT matrix"
