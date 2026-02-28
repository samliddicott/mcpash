#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE_FILE="${1:-${ROOT}/docs/reports/perf-baseline.json}"
CURRENT_FILE="${2:-}"
MAX_REGRESSION="${PERF_MAX_REGRESSION:-1.25}"
MIN_DELTA_MS="${PERF_MIN_DELTA_MS:-5.0}"

if [[ ! -f "$BASELINE_FILE" ]]; then
  echo "[FAIL] baseline file not found: $BASELINE_FILE" >&2
  exit 1
fi

tmp_current=""
cleanup() {
  if [[ -n "$tmp_current" && -f "$tmp_current" ]]; then
    rm -f "$tmp_current"
  fi
}
trap cleanup EXIT

if [[ -z "$CURRENT_FILE" ]]; then
  tmp_current="$(mktemp)"
  "$ROOT/scripts/benchmark_parity.sh" "$tmp_current" >/dev/null
  CURRENT_FILE="$tmp_current"
fi

if [[ ! -f "$CURRENT_FILE" ]]; then
  echo "[FAIL] current benchmark file not found: $CURRENT_FILE" >&2
  exit 1
fi

BASELINE_FILE="$BASELINE_FILE" CURRENT_FILE="$CURRENT_FILE" MAX_REGRESSION="$MAX_REGRESSION" MIN_DELTA_MS="$MIN_DELTA_MS" python3 - <<'PY'
import json
import os
import sys

baseline_file = os.environ["BASELINE_FILE"]
current_file = os.environ["CURRENT_FILE"]
max_regression = float(os.environ["MAX_REGRESSION"])
min_delta_ms = float(os.environ["MIN_DELTA_MS"])

with open(baseline_file, "r", encoding="utf-8") as f:
    baseline = json.load(f)
with open(current_file, "r", encoding="utf-8") as f:
    current = json.load(f)

def by_name(doc):
    out = {}
    for w in doc.get("workloads", []):
        if w.get("ok") and "median_ms" in w:
            out[w["name"]] = w
    return out

b = by_name(baseline)
c = by_name(current)

if not b:
    print("[FAIL] baseline has no successful workloads", file=sys.stderr)
    sys.exit(1)

missing = sorted(set(b.keys()) - set(c.keys()))
if missing:
    print(f"[FAIL] current run missing workloads: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

failed = []
for name in sorted(b.keys()):
    bmed = float(b[name]["median_ms"])
    cmed = float(c[name]["median_ms"])
    ratio = (cmed / bmed) if bmed > 0 else 1.0
    delta = cmed - bmed
    print(f"[INFO] {name}: baseline={bmed:.2f}ms current={cmed:.2f}ms ratio={ratio:.3f} delta={delta:.2f}ms")
    if ratio > max_regression and delta > min_delta_ms:
        failed.append((name, ratio, delta))

if failed:
    for name, ratio, delta in failed:
        print(f"[FAIL] regression {name}: ratio={ratio:.3f} delta={delta:.2f}ms", file=sys.stderr)
    sys.exit(1)

print("[PASS] performance compare within thresholds")
PY
