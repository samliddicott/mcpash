#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_FILE="${1:-${ROOT}/docs/reports/perf-variation.json}"
BATCHES="${PERF_VARIATION_BATCHES:-8}"
RUNS_PER_BATCH="${PERF_VARIATION_RUNS_PER_BATCH:-5}"

if (( BATCHES < 2 )); then
  echo "[FAIL] PERF_VARIATION_BATCHES must be >= 2" >&2
  exit 1
fi

tmpdir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

mkdir -p "$(dirname "$OUT_FILE")"

for ((i=1; i<=BATCHES; i++)); do
  PERF_RUNS="$RUNS_PER_BATCH" PERF_INCLUDE_BUSYBOX="${PERF_INCLUDE_BUSYBOX:-0}" \
    "$ROOT/scripts/benchmark_parity.sh" "$tmpdir/batch-$i.json" >/dev/null
done

ROOT="$ROOT" OUT_FILE="$OUT_FILE" TMPDIR_IN="$tmpdir" BATCHES="$BATCHES" RUNS_PER_BATCH="$RUNS_PER_BATCH" python3 - <<'PY'
import glob
import json
import os
import statistics
from datetime import datetime, timezone

tmpdir = os.environ["TMPDIR_IN"]
out_file = os.environ["OUT_FILE"]
batches = int(os.environ["BATCHES"])
runs_per_batch = int(os.environ["RUNS_PER_BATCH"])

docs = []
for p in sorted(glob.glob(os.path.join(tmpdir, "batch-*.json"))):
    with open(p, "r", encoding="utf-8") as f:
        docs.append(json.load(f))

if len(docs) != batches:
    raise SystemExit(f"expected {batches} batch files, got {len(docs)}")

series = {}
for d in docs:
    for w in d.get("workloads", []):
        if not w.get("ok"):
            continue
        name = w["name"]
        series.setdefault(name, []).append(float(w["median_ms"]))

variation = []
for name in sorted(series):
    medians = series[name]
    base = statistics.median(medians)
    stdev = statistics.pstdev(medians) if len(medians) > 1 else 0.0
    cv = (stdev / base) if base > 0 else 0.0
    variation.append(
        {
            "name": name,
            "batch_medians_ms": medians,
            "median_of_medians_ms": base,
            "min_batch_median_ms": min(medians),
            "max_batch_median_ms": max(medians),
            "spread_ms": max(medians) - min(medians),
            "stddev_ms": stdev,
            "cv": cv,
        }
    )

payload = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "batches": batches,
    "runs_per_batch": runs_per_batch,
    "variation": variation,
}

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, sort_keys=True)
    f.write("\n")
print(f"[INFO] wrote variation report: {out_file}")
for v in variation:
    print(
        f"[INFO] {v['name']}: median={v['median_of_medians_ms']:.2f}ms "
        f"spread={v['spread_ms']:.2f}ms cv={v['cv']:.4f}"
    )
PY
