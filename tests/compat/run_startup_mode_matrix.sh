#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

# default bash mode
set +e
env -u BASH_COMPAT PYTHONPATH="$ROOT/src" python3 -m mctash -c 'set -o | sed -n "s/^posix[[:space:]]*//p"; echo "compat:${BASH_COMPAT}"' >"$tmpdir/out" 2>"$tmpdir/err"
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "default mode rc=$rc"
grep -Fxq 'off' "$tmpdir/out" || fail "default mode expected posix off"
grep -Fxq 'compat:50' "$tmpdir/out" || fail "default mode expected compat:50"

# explicit posix
set +e
env -u BASH_COMPAT PYTHONPATH="$ROOT/src" python3 -m mctash --posix -c 'set -o | sed -n "s/^posix[[:space:]]*//p"; echo "compat:${BASH_COMPAT}"' >"$tmpdir/out" 2>"$tmpdir/err"
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "--posix rc=$rc"
grep -Fxq 'on' "$tmpdir/out" || fail "--posix expected posix on"
grep -Fxq 'compat:' "$tmpdir/out" || fail "--posix expected empty compat"

# argv0 mode sh/ash => posix
set +e
env -u BASH_COMPAT MCTASH_ARG0=sh PYTHONPATH="$ROOT/src" python3 -m mctash -c 'set -o | sed -n "s/^posix[[:space:]]*//p"; echo "compat:${BASH_COMPAT}"' >"$tmpdir/out" 2>"$tmpdir/err"
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "arg0 sh rc=$rc"
grep -Fxq 'on' "$tmpdir/out" || fail "arg0 sh expected posix on"
grep -Fxq 'compat:' "$tmpdir/out" || fail "arg0 sh expected empty compat"

# bash-mode BASH_ENV non-interactive preload
mkdir -p "$tmpdir/home"
cat >"$tmpdir/home/bash_env.sh" <<'EOS'
echo STARTUP_BASH_ENV
EOS
set +e
HOME="$tmpdir/home" MCTASH_MODE=bash BASH_ENV="$tmpdir/home/bash_env.sh" PYTHONPATH="$ROOT/src" python3 -m mctash -c 'echo BODY' >"$tmpdir/out" 2>"$tmpdir/err"
rc=$?
set -e
[[ "$rc" -eq 0 ]] || fail "BASH_ENV preload rc=$rc"
grep -Fxq 'STARTUP_BASH_ENV' "$tmpdir/out" || fail "missing BASH_ENV preload output"
grep -Fxq 'BODY' "$tmpdir/out" || fail "missing body output"

# restricted mode startup
set +e
PYTHONPATH="$ROOT/src" python3 -m mctash -r -c '/bin/echo hi' >"$tmpdir/out" 2>"$tmpdir/err"
rc=$?
set -e
[[ "$rc" -eq 1 ]] || fail "restricted slash command expected rc=1 got $rc"
grep -Fq "cannot specify \`/' in command names" "$tmpdir/err" || fail "restricted diagnostic missing"

echo "[PASS] startup mode matrix"
