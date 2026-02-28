#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPEATS="${RACE_REPEATS:-100}"
MODES="${RACE_UNSHARE_MODES:-auto}"
FAIL_FAST="${RACE_FAIL_FAST:-1}"

tmpdir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

run_once() {
  local name="$1"
  local script="$2"
  local expect_status="$3"
  local expect_stdout="$4"
  local expect_stderr_substr="${5:-}"
  local mode="$6"
  local iter="$7"

  local out="$tmpdir/${name}.${mode}.${iter}.out"
  local err="$tmpdir/${name}.${mode}.${iter}.err"

  set +e
  PYTHONPATH="$ROOT/src" MCTASH_TEST_MODE=1 MCTASH_UNSHARE_MODE="$mode" python3 -m mctash -c "$script" >"$out" 2>"$err"
  local rc=$?
  set -e

  if [[ "$rc" -ne "$expect_status" ]]; then
    echo "[FAIL] ${name} mode=${mode} iter=${iter}: status ${rc} != ${expect_status}" >&2
    sed 's/^/  /' "$out" >&2 || true
    sed 's/^/  /' "$err" >&2 || true
    return 1
  fi
  local got
  got="$(cat "$out")"
  if [[ "$got"$'\n' != "$expect_stdout" ]]; then
    echo "[FAIL] ${name} mode=${mode} iter=${iter}: stdout mismatch" >&2
    echo "  expected: $(printf %q "$expect_stdout")" >&2
    echo "  got:      $(printf %q "$got"$'\n')" >&2
    sed 's/^/  /' "$err" >&2 || true
    return 1
  fi
  if [[ -n "$expect_stderr_substr" ]] && ! grep -Fq "$expect_stderr_substr" "$err"; then
    echo "[FAIL] ${name} mode=${mode} iter=${iter}: stderr missing '$expect_stderr_substr'" >&2
    sed 's/^/  /' "$err" >&2 || true
    return 1
  fi
  return 0
}

IFS=',' read -r -a mode_list <<<"$MODES"
total_checks=0
total_failures=0

for mode in "${mode_list[@]}"; do
  mode="${mode// /}"
  [[ -n "$mode" ]] || continue
  echo "[INFO] mode=${mode} repeats=${REPEATS}"
  for ((i=1; i<=REPEATS; i++)); do
    total_checks=$((total_checks + 1))
    if ! run_once \
      "thread_multi_job_concurrency_isolation" \
      'orig="$PWD"; p1="/tmp/mctash-conc-a-$$.txt"; p2="/tmp/mctash-conc-b-$$.txt"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); ( cd /; exec 9>/dev/null; printf "A\n" | cat > >(cat > "$p1") ) & j1=$!; ( cd /tmp; exec 9>/dev/null; printf "B\n" | cat > >(cat > "$p2") ) & j2=$!; wait "$j1"; wait "$j2"; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; [ "$after" = "$orig" ] && c=same || c=diff; data=$(cat "$p1" "$p2" | sort | tr -d "\n"); rm -f "$p1" "$p2"; echo "$pre:$post:$c:$data"' \
      0 \
      $'no:no:same:AB\n' \
      "" \
      "$mode" \
      "$i"; then
      total_failures=$((total_failures + 1))
      [[ "$FAIL_FAST" == "1" ]] && exit 1
    fi

    total_checks=$((total_checks + 1))
    if ! run_once \
      "thread_high_load_concurrency_isolation" \
      'orig="$PWD"; d="/tmp/mctash-stress-$$"; mkdir -p "$d"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); pids=""; for i in 1 2 3 4 5; do ( cd /; exec 9>/dev/null; printf "J$i\n" | cat > >(cat > "$d/$i.out") ) & pids="$pids $!"; done; for p in $pids; do wait "$p"; done; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; [ "$after" = "$orig" ] && c=same || c=diff; count=$(cat "$d"/*.out | wc -l | tr -d " "); miss=0; for i in 1 2 3 4 5; do grep -qx "J$i" "$d/$i.out" || miss=$((miss+1)); done; rm -rf "$d"; echo "$pre:$post:$c:$count:$miss"' \
      0 \
      $'no:no:same:5:0\n' \
      "" \
      "$mode" \
      "$i"; then
      total_failures=$((total_failures + 1))
      [[ "$FAIL_FAST" == "1" ]] && exit 1
    fi

    total_checks=$((total_checks + 1))
    if ! run_once \
      "thread_long_running_mixed_stress" \
      'orig="$PWD"; base="/tmp/mctash-stress2-$$"; rm -rf "$base"; mkdir -p "$base"; pre=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); miss=0; total=0; for r in 1 2 3 4 5 6; do d="$base/$r"; mkdir -p "$d"; pids=""; for i in 1 2 3; do ( cd /; exec 9>/dev/null; printf "R${r}J${i}\n" | cat > >(cat > "$d/$i.out") ) & pids="$pids $!"; done; for p in $pids; do wait "$p"; done; for i in 1 2 3; do total=$((total+1)); grep -qx "R${r}J${i}" "$d/$i.out" || miss=$((miss+1)); done; done; post=$( [ -e /proc/$$/fd/9 ] && echo yes || echo no ); after="$PWD"; [ "$after" = "$orig" ] && c=same || c=diff; rm -rf "$base"; echo "$pre:$post:$c:$miss:$total"' \
      0 \
      $'no:no:same:0:18\n' \
      "" \
      "$mode" \
      "$i"; then
      total_failures=$((total_failures + 1))
      [[ "$FAIL_FAST" == "1" ]] && exit 1
    fi

    if (( i % 10 == 0 )) || (( i == REPEATS )); then
      echo "[INFO] mode=${mode} progress=${i}/${REPEATS}"
    fi
  done
done

pass_count=$((total_checks - total_failures))
echo "[INFO] stress-race summary checks=${total_checks} pass=${pass_count} fail=${total_failures}"
if (( total_failures > 0 )); then
  echo "[FAIL] stress-race detected intermittent correctness failures"
  exit 1
fi
echo "[PASS] stress-race strict pass (${REPEATS} repeats x modes: ${MODES})"
