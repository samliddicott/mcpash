#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE_FILE="${1:-${ROOT}/docs/reports/perf-baseline.json}"
CURRENT_FILE="${2:-}"
THRESHOLDS_FILE="${PERF_THRESHOLDS_FILE:-${ROOT}/docs/reports/perf-thresholds.json}"
MAX_REGRESSION="${PERF_MAX_REGRESSION:-}"
MIN_DELTA_MS="${PERF_MIN_DELTA_MS:-}"

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

BASELINE_FILE="$BASELINE_FILE" CURRENT_FILE="$CURRENT_FILE" THRESHOLDS_FILE="$THRESHOLDS_FILE" MAX_REGRESSION="$MAX_REGRESSION" MIN_DELTA_MS="$MIN_DELTA_MS" python3 - <<'PY'
import json
import os
import sys

baseline_file = os.environ["BASELINE_FILE"]
current_file = os.environ["CURRENT_FILE"]
thresholds_file = os.environ["THRESHOLDS_FILE"]
max_regression_override = os.environ.get("MAX_REGRESSION", "").strip()
min_delta_ms_override = os.environ.get("MIN_DELTA_MS", "").strip()

with open(baseline_file, "r", encoding="utf-8") as f:
    baseline = json.load(f)
with open(current_file, "r", encoding="utf-8") as f:
    current = json.load(f)

thresholds = {"default": {"max_regression_ratio": 1.25, "min_delta_ms": 5.0}, "workloads": {}}
if os.path.exists(thresholds_file):
    with open(thresholds_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    if isinstance(loaded, dict):
        thresholds.update(loaded)

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
    spec = thresholds.get("workloads", {}).get(name, {})
    max_regression = float(max_regression_override or spec.get("max_regression_ratio", thresholds["default"]["max_regression_ratio"]))
    min_delta_ms = float(min_delta_ms_override or spec.get("min_delta_ms", thresholds["default"]["min_delta_ms"]))
    print(
        f"[INFO] {name}: baseline={bmed:.2f}ms current={cmed:.2f}ms "
        f"ratio={ratio:.3f} delta={delta:.2f}ms "
        f"limits(ratio<={max_regression:.3f}, delta<={min_delta_ms:.2f}ms)"
    )
    if ratio > max_regression and delta > min_delta_ms:
        failed.append((name, ratio, delta, max_regression, min_delta_ms))

if failed:
    for name, ratio, delta, mr, md in failed:
        print(
            f"[FAIL] regression {name}: ratio={ratio:.3f}>{mr:.3f} and delta={delta:.2f}ms>{md:.2f}ms",
            file=sys.stderr,
        )
    sys.exit(1)

print("[PASS] performance compare within thresholds")
PY
