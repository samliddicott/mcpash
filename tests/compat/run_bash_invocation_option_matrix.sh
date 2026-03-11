#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
home="$tmpdir/home"
mkdir -p "$home"
cat >"$home/.bash_profile" <<'EOF'
: > "$HOME/profile.marker"
EOF
cat >"$home/.bashrc" <<'EOF'
: > "$HOME/bashrc.marker"
EOF
cat >"$home/custom.rc" <<'EOF'
: > "$HOME/customrc.marker"
EOF
cat >"$tmpdir/-sentinel" <<'EOF'
echo "sentinel:$0:$#:$1"
EOF

run_cmd() {
  local name=$1
  local mode=$2
  local shell_kind=$3
  local stdin_text=$4
  shift 4
  local out="$tmpdir/${name}.${mode}.${shell_kind}.out"
  local err="$tmpdir/${name}.${mode}.${shell_kind}.err"
  local rc="$tmpdir/${name}.${mode}.${shell_kind}.rc"
  local -a cmd=()
  if [[ "$shell_kind" == "bash" ]]; then
    cmd=(env HOME="$home" bash)
    [[ "$mode" == "posix" ]] && cmd+=(--posix)
  else
    cmd=(env HOME="$home" PYTHONPATH="$ROOT/src" MCTASH_MODE=bash python3 -m mctash)
    [[ "$mode" == "posix" ]] && cmd+=(--posix)
  fi
  cmd+=("$@")
  set +e
  if [[ -n "$stdin_text" ]]; then
    (
      cd "$tmpdir"
      printf '%s' "$stdin_text" | "${cmd[@]}"
    ) >"$out" 2>"$err"
  else
    (
      cd "$tmpdir"
      "${cmd[@]}"
    ) >"$out" 2>"$err"
  fi
  echo "$?" >"$rc"
  set -e
}

compare_case() {
  local name=$1
  local mode=$2
  local stdin_text=$3
  shift 3
  run_cmd "$name" "$mode" bash "$stdin_text" "$@"
  run_cmd "$name" "$mode" mctash "$stdin_text" "$@"
  local brc mrc
  brc=$(cat "$tmpdir/${name}.${mode}.bash.rc")
  mrc=$(cat "$tmpdir/${name}.${mode}.mctash.rc")
  local ok=1
  if [[ "$brc" != "$mrc" ]]; then
    echo "[MISMATCH] $name/$mode rc bash=$brc mctash=$mrc"
    ok=0
  fi
  if ! diff -u "$tmpdir/${name}.${mode}.bash.out" "$tmpdir/${name}.${mode}.mctash.out" >/dev/null; then
    echo "[MISMATCH] $name/$mode stdout"
    ok=0
  fi
  if ! diff -u "$tmpdir/${name}.${mode}.bash.err" "$tmpdir/${name}.${mode}.mctash.err" >/dev/null; then
    echo "[MISMATCH] $name/$mode stderr"
    ok=0
  fi
  return $((ok ? 0 : 1))
}

compare_case_status_only() {
  local name=$1
  local mode=$2
  local stdin_text=$3
  shift 3
  run_cmd "$name" "$mode" bash "$stdin_text" "$@"
  run_cmd "$name" "$mode" mctash "$stdin_text" "$@"
  local brc mrc
  brc=$(cat "$tmpdir/${name}.${mode}.bash.rc")
  mrc=$(cat "$tmpdir/${name}.${mode}.mctash.rc")
  if [[ "$brc" != "$mrc" ]]; then
    echo "[MISMATCH] $name/$mode rc bash=$brc mctash=$mrc"
    return 1
  fi
  return 0
}

fail=0
for mode in bash posix; do
  rm -f "$home"/{profile.marker,bashrc.marker,customrc.marker}
  compare_case short-c "$mode" '' -c 'echo c:ok' || fail=1
  compare_case short-v "$mode" '' -v -c 'echo v:ok' || fail=1
  compare_case short-x "$mode" '' -x -c 'echo x:ok' || fail=1
  compare_case short-s-with-args "$mode" 'echo "s:$1:$2:$#"\n' -s A B || fail=1
  compare_case long-verbose "$mode" '' --verbose -c 'echo verbose:ok' || fail=1
  compare_case short-D "$mode" '' -D -c 'echo $"hello"' || fail=1
  compare_case long-dump-strings "$mode" '' --dump-strings -c 'echo $"hello"' || fail=1
  compare_case long-dump-po "$mode" '' --dump-po-strings -c 'echo $"hello"' || fail=1
  compare_case_status_only long-help "$mode" '' --help || fail=1
  compare_case_status_only long-version "$mode" '' --version || fail=1
  compare_case_status_only long-login "$mode" '' --login --noprofile -c 'echo login:ok' || fail=1
  compare_case_status_only long-noprofile "$mode" '' --login --noprofile -c 'echo noprofile:ok' || fail=1
  compare_case_status_only long-norc "$mode" '' --norc -c 'echo norc:ok' || fail=1
  compare_case_status_only long-noediting "$mode" '' --noediting -c 'echo noediting:ok' || fail=1
  compare_case_status_only long-restricted "$mode" '' --restricted -c 'echo restricted:ok' || fail=1
  compare_case_status_only short-O "$mode" '' -O extglob -c 'shopt -q extglob; echo rc:$?' || fail=1
  compare_case_status_only short-plusO "$mode" '' +O extglob -c 'shopt -q extglob; echo rc:$?' || fail=1
  compare_case short-dashdash "$mode" '' -- -sentinel ARG || fail=1
  compare_case short-singledash "$mode" '' - -sentinel ARG || fail=1
  compare_case_status_only short-l "$mode" '' -l -c '[ -f "$HOME/profile.marker" ]' || fail=1
  rm -f "$home/customrc.marker"
  compare_case_status_only long-rcfile-file "$mode" '' --rcfile "$home/custom.rc" -i -c '[ -f "$HOME/customrc.marker" ]' || fail=1
  rm -f "$home/customrc.marker"
  compare_case_status_only long-init-file-file "$mode" '' --init-file "$home/custom.rc" -i -c '[ -f "$HOME/customrc.marker" ]' || fail=1
  compare_case_status_only short-i "$mode" '' -i -c 'echo i:ok' || fail=1
  compare_case_status_only short-r "$mode" '' -r -c 'echo r:ok' || fail=1
  compare_case_status_only long-posix "$mode" '' --posix -c 'echo posix:ok' || fail=1
done

if [[ $fail -ne 0 ]]; then
  echo "[FAIL] invocation option matrix"
  exit 1
fi

echo "[PASS] invocation option matrix"
