#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BUSYBOX_MIN_OK="${BUSYBOX_MIN_OK:-357}"
BUSYBOX_MAX_FAIL="${BUSYBOX_MAX_FAIL:-0}"
BUSYBOX_ALLOWED_FAIL_FILES="${BUSYBOX_ALLOWED_FAIL_FILES:-ash-signals-sigquit_exec.tests.fail}"
RUN_TIMEOUT="${RUN_TIMEOUT:-1200}"

OIL_MIN_PASS="${OIL_MIN_PASS:-244}"
OIL_MAX_FAIL="${OIL_MAX_FAIL:-1}"
OIL_SPECS=(
  smoke
  redirect
  word-split
  posix
  shell-grammar
  sh-options
  command-parsing
  loop
  if_
  case_
  var-op-strip
  var-op-test
  var-sub
  pipeline
  command_
)

tmpdir="$(mktemp -d)"
keep_tmp=0
cleanup() {
  if (( keep_tmp == 0 )); then
    rm -rf "$tmpdir"
  else
    info "Preserving logs in $tmpdir"
  fi
}
trap cleanup EXIT

pass() { printf '[PASS] %s\n' "$*"; }
fail() {
  keep_tmp=1
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}
info() { printf '[INFO] %s\n' "$*"; }

info "Running targeted regressions"
"$ROOT/tests/regressions/run.sh"
pass "Targeted regressions"

info "Running BusyBox ash corpus (timeout=${RUN_TIMEOUT}s)"
busy_log="$tmpdir/busybox.log"
busy_rc=0
if ! RUN_TIMEOUT="$RUN_TIMEOUT" "$ROOT/src/tests/run_busybox_ash.sh" run >"$busy_log" 2>&1; then
  busy_rc=$?
fi
busy_summary="$(grep 'Summary:' "$busy_log" | tail -n1 || true)"
[[ -n "$busy_summary" ]] || fail "BusyBox run produced no summary. See $busy_log"
busy_ok="$(printf '%s\n' "$busy_summary" | sed -n 's/.*ok=\([0-9][0-9]*\).*/\1/p')"
busy_fail="$(printf '%s\n' "$busy_summary" | sed -n 's/.*fail=\([0-9][0-9]*\).*/\1/p')"
busy_skip="$(printf '%s\n' "$busy_summary" | sed -n 's/.*skip=\([0-9][0-9]*\).*/\1/p')"
info "BusyBox summary: ok=${busy_ok} fail=${busy_fail} skip=${busy_skip} rc=${busy_rc}"
[[ "${busy_ok:-}" =~ ^[0-9]+$ ]] || fail "Could not parse BusyBox ok count"
[[ "${busy_fail:-}" =~ ^[0-9]+$ ]] || fail "Could not parse BusyBox fail count"
if (( busy_rc != 0 )); then
  fail "BusyBox run exited non-zero (${busy_rc}). See $busy_log"
fi
allowed_hits=0
if [[ -n "$BUSYBOX_ALLOWED_FAIL_FILES" ]]; then
  IFS=',' read -r -a allowed_list <<<"$BUSYBOX_ALLOWED_FAIL_FILES"
  for fail_path in "$ROOT"/tests/busybox/ash_test/*.fail; do
    [[ -e "$fail_path" ]] || continue
    base="$(basename "$fail_path")"
    for allowed in "${allowed_list[@]}"; do
      if [[ "$base" == "$allowed" ]]; then
        allowed_hits=$((allowed_hits + 1))
        break
      fi
    done
  done
fi
effective_busy_fail=$((busy_fail - allowed_hits))
if (( effective_busy_fail < 0 )); then
  effective_busy_fail=0
fi
if (( effective_busy_fail > BUSYBOX_MAX_FAIL )); then
  fail "BusyBox fail count ${busy_fail} (effective ${effective_busy_fail}) exceeded threshold ${BUSYBOX_MAX_FAIL}"
fi
effective_busy_min_ok=$((BUSYBOX_MIN_OK - allowed_hits))
if (( effective_busy_min_ok < 0 )); then
  effective_busy_min_ok=0
fi
if (( busy_ok < effective_busy_min_ok )); then
  fail "BusyBox ok count ${busy_ok} below minimum ${effective_busy_min_ok} (base ${BUSYBOX_MIN_OK})"
fi
pass "BusyBox conformance gate (effective_fail=${effective_busy_fail})"

info "Running Oil subset corpus"
oil_log="$tmpdir/oil.log"
oil_rc=0
if ! "$ROOT/src/tests/run_oil_subset.sh" run "${OIL_SPECS[@]}" >"$oil_log" 2>&1; then
  oil_rc=$?
fi
oil_summary="$(grep '^SUMMARY ' "$oil_log" | tail -n1 || true)"
[[ -n "$oil_summary" ]] || fail "Oil run produced no SUMMARY line. See $oil_log"
oil_total="$(printf '%s\n' "$oil_summary" | sed -n 's/.*total=\([0-9][0-9]*\).*/\1/p')"
oil_pass="$(printf '%s\n' "$oil_summary" | sed -n 's/.*pass=\([0-9][0-9]*\).*/\1/p')"
oil_fail="$(printf '%s\n' "$oil_summary" | sed -n 's/.*fail=\([0-9][0-9]*\).*/\1/p')"
oil_skip="$(printf '%s\n' "$oil_summary" | sed -n 's/.*skip=\([0-9][0-9]*\).*/\1/p')"
info "Oil summary: total=${oil_total} pass=${oil_pass} fail=${oil_fail} skip=${oil_skip} rc=${oil_rc}"
[[ "${oil_pass:-}" =~ ^[0-9]+$ ]] || fail "Could not parse Oil pass count"
[[ "${oil_fail:-}" =~ ^[0-9]+$ ]] || fail "Could not parse Oil fail count"
if (( oil_fail > OIL_MAX_FAIL )); then
  fail "Oil fail count ${oil_fail} exceeded threshold ${OIL_MAX_FAIL}"
fi
if (( oil_pass < OIL_MIN_PASS )); then
  fail "Oil pass count ${oil_pass} below minimum ${OIL_MIN_PASS}"
fi
pass "Oil conformance gate"

pass "Conformance gate complete"
