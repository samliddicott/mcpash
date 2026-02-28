#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_FILE="${1:-${ROOT}/docs/reports/perf-baseline.json}"
RUNS="${PERF_RUNS:-7}"
INCLUDE_BUSYBOX="${PERF_INCLUDE_BUSYBOX:-0}"

mkdir -p "$(dirname "$OUT_FILE")"

ROOT="$ROOT" OUT_FILE="$OUT_FILE" RUNS="$RUNS" INCLUDE_BUSYBOX="$INCLUDE_BUSYBOX" python3 - <<'PY'
import json
import os
import platform
import socket
import statistics
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["ROOT"])
out_file = Path(os.environ["OUT_FILE"])
runs = max(1, int(os.environ["RUNS"]))
include_busybox = os.environ.get("INCLUDE_BUSYBOX", "0") == "1"

env = dict(os.environ)
env["PYTHONPATH"] = str(root / "src")
env["MCTASH_TEST_MODE"] = "1"


def run_cmd(argv: list[str], cwd: Path | None = None) -> tuple[int, float]:
    t0 = time.perf_counter()
    p = subprocess.run(argv, cwd=str(cwd or root), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t1 = time.perf_counter()
    return p.returncode, (t1 - t0) * 1000.0


def bench(name: str, argv: list[str], *, cwd: Path | None = None, expect_rc: int = 0) -> dict:
    samples: list[float] = []
    rc_fail = None
    for _ in range(runs):
        rc, ms = run_cmd(argv, cwd=cwd)
        if rc != expect_rc:
            rc_fail = rc
            break
        samples.append(ms)
    if rc_fail is not None:
        return {"name": name, "ok": False, "rc": rc_fail, "argv": argv, "samples_ms": []}
    p95 = sorted(samples)[max(0, int(len(samples) * 0.95) - 1)]
    return {
        "name": name,
        "ok": True,
        "rc": 0,
        "argv": argv,
        "samples_ms": samples,
        "median_ms": statistics.median(samples),
        "mean_ms": statistics.fmean(samples),
        "p95_ms": p95,
        "min_ms": min(samples),
        "max_ms": max(samples),
    }


with tempfile.TemporaryDirectory(prefix="mctash-perf-") as td:
    td_path = Path(td)
    small_script = td_path / "small.sh"
    small_script.write_text("x=1\ny=2\necho $((x+y)) >/dev/null\n", encoding="utf-8")

    pipe_script = td_path / "pipe.sh"
    pipe_script.write_text(
        "i=0\nwhile [ $i -lt 40 ]; do\n"
        "  printf 'a b c\\n' | tr ' ' '_' | sed 's/c/C/' >/dev/null\n"
        "  i=$((i+1))\ndone\n",
        encoding="utf-8",
    )

    bridge_script = td_path / "bridge.sh"
    bridge_script.write_text(
        "py 'x=1'\n"
        "py -e 'x+2' >/dev/null\n"
        "PYTHON\n"
        "for i in range(10):\n"
        "    pass\n"
        "END_PYTHON\n",
        encoding="utf-8",
    )

    workloads = [
        bench("cold_start", ["python3", "-m", "mctash", "-c", ":"], cwd=root),
        bench("small_script", ["python3", "-m", "mctash", str(small_script)], cwd=root),
        bench("pipeline_heavy", ["python3", "-m", "mctash", str(pipe_script)], cwd=root),
        bench("bridge_heavy", ["python3", "-m", "mctash", str(bridge_script)], cwd=root),
        bench(
            "diff_subset",
            ["bash", str(root / "tests/diff/run.sh"), "--case", "man-ash-set", "--case", "man-ash-var-ops", "--case", "man-ash-redir"],
            cwd=root,
        ),
    ]

    if include_busybox:
        workloads.append(
            bench(
                "busybox_spotcheck",
                ["bash", str(root / "src/tests/run_busybox_ash.sh"), "run", "ash-glob", "ash-read"],
                cwd=root,
            )
        )

git_commit = ""
try:
    git_commit = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(root), stderr=subprocess.DEVNULL, text=True).strip()
    )
except Exception:
    git_commit = ""

payload = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "host": socket.gethostname(),
    "platform": platform.platform(),
    "python_version": platform.python_version(),
    "git_commit": git_commit,
    "runs_per_workload": runs,
    "include_busybox_spotcheck": include_busybox,
    "workloads": workloads,
}

out_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"[INFO] wrote benchmark: {out_file}")
PY
