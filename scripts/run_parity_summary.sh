#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUMMARY_FILE="${1:-${ROOT}/docs/reports/parity-summary.json}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TS_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LOG_DIR="${ROOT}/docs/reports/parity-logs/${STAMP}"

mkdir -p "$LOG_DIR" "$(dirname "$SUMMARY_FILE")"

run_step() {
  local name="$1"
  shift
  local log="${LOG_DIR}/${name}.log"
  local rc=0
  set +e
  "$@" >"$log" 2>&1
  rc=$?
  set -e
  printf '[INFO] %-10s rc=%s log=%s\n' "$name" "$rc" "$log" >&2
  return "$rc"
}

bridge_rc=0
diff_rc=0
busybox_raw_rc=0

set +e
run_step bridge "$ROOT/tests/bridge/run.sh"
bridge_rc=$?
set -e

set +e
run_step diff "$ROOT/tests/diff/run.sh"
diff_rc=$?
set -e

set +e
run_step busybox env RUN_TIMEOUT="${RUN_TIMEOUT:-1200}" RUN_MODULE_TIMEOUT="${RUN_MODULE_TIMEOUT:-1200}" "$ROOT/src/tests/run_busybox_ash.sh" run
busybox_raw_rc=$?
set -e

busybox_summary="$(grep 'Summary:' "${LOG_DIR}/busybox.log" | tail -n1 || true)"
busybox_ok="$(printf '%s\n' "$busybox_summary" | sed -n 's/.*ok=\([0-9][0-9]*\).*/\1/p')"
busybox_fail="$(printf '%s\n' "$busybox_summary" | sed -n 's/.*fail=\([0-9][0-9]*\).*/\1/p')"
busybox_skip="$(printf '%s\n' "$busybox_summary" | sed -n 's/.*skip=\([0-9][0-9]*\).*/\1/p')"

BUSYBOX_MIN_OK="${BUSYBOX_MIN_OK:-357}"
BUSYBOX_MAX_FAIL="${BUSYBOX_MAX_FAIL:-0}"
BUSYBOX_ALLOWED_FAIL_FILES="${BUSYBOX_ALLOWED_FAIL_FILES:-ash-signals-sigquit_exec.tests.fail}"

allowed_hits=0
unexpected_busy=()
if [[ -n "$BUSYBOX_ALLOWED_FAIL_FILES" ]]; then
  IFS=',' read -r -a allowed_list <<<"$BUSYBOX_ALLOWED_FAIL_FILES"
else
  allowed_list=()
fi
for fail_path in "$ROOT"/tests/busybox/ash_test/*.fail; do
  [[ -e "$fail_path" ]] || continue
  base="$(basename "$fail_path")"
  matched=0
  for allowed in "${allowed_list[@]}"; do
    if [[ -n "$allowed" && "$base" == "$allowed" ]]; then
      allowed_hits=$((allowed_hits + 1))
      matched=1
      break
    fi
  done
  if (( matched == 0 )); then
    unexpected_busy+=("$base")
  fi
done

effective_busy_fail=0
effective_busy_min_ok="$BUSYBOX_MIN_OK"
busybox_step_ok=0
if [[ "$busybox_ok" =~ ^[0-9]+$ && "$busybox_fail" =~ ^[0-9]+$ ]]; then
  effective_busy_fail=$((busybox_fail - allowed_hits))
  if (( effective_busy_fail < 0 )); then
    effective_busy_fail=0
  fi
  effective_busy_min_ok=$((BUSYBOX_MIN_OK - allowed_hits))
  if (( effective_busy_min_ok < 0 )); then
    effective_busy_min_ok=0
  fi
  if (( ${#unexpected_busy[@]} == 0 )) && (( effective_busy_fail <= BUSYBOX_MAX_FAIL )) && (( busybox_ok >= effective_busy_min_ok )); then
    busybox_step_ok=1
  fi
fi

overall_rc=0
if [[ "$bridge_rc" -ne 0 || "$diff_rc" -ne 0 || "$busybox_step_ok" -ne 1 ]]; then
  overall_rc=1
fi

SUMMARY_FILE="$SUMMARY_FILE" TS_UTC="$TS_UTC" LOG_DIR="$LOG_DIR" \
BRIDGE_RC="$bridge_rc" DIFF_RC="$diff_rc" BUSYBOX_RAW_RC="$busybox_raw_rc" BUSYBOX_STEP_OK="$busybox_step_ok" \
BUSYBOX_SUMMARY="$busybox_summary" BUSYBOX_OK="${busybox_ok:-}" BUSYBOX_FAIL="${busybox_fail:-}" BUSYBOX_SKIP="${busybox_skip:-}" \
BUSYBOX_ALLOWED_HITS="$allowed_hits" BUSYBOX_ALLOWED_LIST="$BUSYBOX_ALLOWED_FAIL_FILES" \
BUSYBOX_EFFECTIVE_FAIL="$effective_busy_fail" BUSYBOX_EFFECTIVE_MIN_OK="$effective_busy_min_ok" \
BUSYBOX_THRESHOLD_FAIL="$BUSYBOX_MAX_FAIL" BUSYBOX_THRESHOLD_MIN_OK="$BUSYBOX_MIN_OK" \
BUSYBOX_UNEXPECTED="${unexpected_busy[*]-}" \
OVERALL_RC="$overall_rc" \
python3 - <<'PY'
import json
import os

def as_int_or_none(s: str):
    try:
        return int(s)
    except Exception:
        return None

payload = {
    "timestamp_utc": os.environ["TS_UTC"],
    "log_dir": os.environ["LOG_DIR"],
    "steps": {
        "bridge": {"rc": int(os.environ["BRIDGE_RC"]), "ok": int(os.environ["BRIDGE_RC"]) == 0},
        "diff": {"rc": int(os.environ["DIFF_RC"]), "ok": int(os.environ["DIFF_RC"]) == 0},
        "busybox": {
            "rc": int(os.environ["BUSYBOX_RAW_RC"]),
            "ok": int(os.environ["BUSYBOX_STEP_OK"]) == 1,
            "summary_line": os.environ["BUSYBOX_SUMMARY"],
            "ok_count": as_int_or_none(os.environ.get("BUSYBOX_OK", "")),
            "fail_count": as_int_or_none(os.environ.get("BUSYBOX_FAIL", "")),
            "skip_count": as_int_or_none(os.environ.get("BUSYBOX_SKIP", "")),
            "allowed_fail_files": [x for x in os.environ.get("BUSYBOX_ALLOWED_LIST", "").split(",") if x],
            "allowed_hits": as_int_or_none(os.environ.get("BUSYBOX_ALLOWED_HITS", "")),
            "effective_fail_count": as_int_or_none(os.environ.get("BUSYBOX_EFFECTIVE_FAIL", "")),
            "effective_min_ok": as_int_or_none(os.environ.get("BUSYBOX_EFFECTIVE_MIN_OK", "")),
            "threshold_fail": as_int_or_none(os.environ.get("BUSYBOX_THRESHOLD_FAIL", "")),
            "threshold_min_ok": as_int_or_none(os.environ.get("BUSYBOX_THRESHOLD_MIN_OK", "")),
            "unexpected_fail_files": [x for x in os.environ.get("BUSYBOX_UNEXPECTED", "").split() if x],
        },
    },
    "overall": {"rc": int(os.environ["OVERALL_RC"]), "ok": int(os.environ["OVERALL_RC"]) == 0},
}

with open(os.environ["SUMMARY_FILE"], "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, sort_keys=True)
    f.write("\n")
PY

printf '[INFO] wrote summary: %s\n' "$SUMMARY_FILE" >&2
exit "$overall_rc"
