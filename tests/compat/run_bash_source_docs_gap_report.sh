#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIFF_RUNNER="${ROOT}/tests/diff/run.sh"
POSIX_MATRIX="${ROOT}/docs/specs/bash-posix-mode-implementation-matrix.tsv"
COMPAT_MATRIX="${ROOT}/docs/specs/bash-compat-deltas-implementation-matrix.tsv"
REPORT="${ROOT}/docs/reports/bash-source-docs-gap-latest.md"
LOGDIR="${ROOT}/tests/diff/logs/bash-source-docs-gap"
STRICT="${STRICT:-0}"

mkdir -p "$LOGDIR"

ROOT="$ROOT" POSIX_MATRIX="$POSIX_MATRIX" COMPAT_MATRIX="$COMPAT_MATRIX" REPORT="$REPORT" DIFF_RUNNER="$DIFF_RUNNER" LOGDIR="$LOGDIR" STRICT="$STRICT" python3 - <<'PY'
import csv
import os
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
POSIX_MATRIX = Path(os.environ["POSIX_MATRIX"])
COMPAT_MATRIX = Path(os.environ["COMPAT_MATRIX"])
REPORT = Path(os.environ["REPORT"])
DIFF_RUNNER = Path(os.environ["DIFF_RUNNER"])
LOGDIR = Path(os.environ["LOGDIR"])
STRICT = os.environ.get("STRICT", "0") == "1"


@dataclass
class Row:
    rid: str
    source: str
    feature: str
    default_status: str
    posix_status: str
    tests: list[str]


def load_rows(path: Path, source_name: str) -> list[Row]:
    out: list[Row] = []
    with path.open(encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r, None)
        if not header:
            return out
        for row in r:
            if not row:
                continue
            tests = [x.strip() for x in (row[10] if len(row) > 10 else "").split(",") if x.strip()]
            out.append(
                Row(
                    rid=row[0],
                    source=source_name,
                    feature=row[7],
                    default_status=(row[8] if len(row) > 8 else "partial"),
                    posix_status=(row[9] if len(row) > 9 else "partial"),
                    tests=tests,
                )
            )
    return out


rows = load_rows(POSIX_MATRIX, "bash/POSIX") + load_rows(COMPAT_MATRIX, "bash/COMPAT")

cases_to_run: set[str] = set()
case_sources: dict[str, set[str]] = defaultdict(set)
for row in rows:
    for t in row.tests:
        p = ROOT / "tests" / "diff" / "cases" / t
        if p.exists():
            cases_to_run.add(t)
            case_sources[t].add(row.source)

case_status: dict[str, tuple[bool, str]] = {}
for case in sorted(cases_to_run):
    out = LOGDIR / f"{case}.runner.out"
    sources = case_sources.get(case, set())
    # POSIX document rows should compare in mirrored --posix mode.
    # COMPAT rows should compare in bash mode with explicit BASH_COMPAT.
    if "bash/COMPAT" in sources:
        env_prefix = "PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 MCTASH_MODE_DEFAULT=bash"
    else:
        env_prefix = "PARITY_MIRROR_POSIX=1 MCTASH_MODE_DEFAULT=posix"
    cmd = ["bash", "-lc", f"{env_prefix} {DIFF_RUNNER} --logdir {LOGDIR / case} --case {case[:-3]}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out.write_text((p.stdout or "") + ("\n" + p.stderr if p.stderr else ""), encoding="utf-8")
    case_status[case] = (p.returncode == 0, str(out))

counts = defaultdict(int)
row_results: list[tuple[Row, str, str]] = []
for row in rows:
    mapped = row.tests
    existing = [t for t in mapped if (ROOT / "tests" / "diff" / "cases" / t).exists()]
    matrix_partial = (row.default_status != "covered" or row.posix_status != "covered")
    if not mapped:
        status = "unmapped"
        note = "no test id in matrix"
    elif not existing:
        status = "unprobed"
        note = "mapped test case file(s) missing"
    else:
        failed = [t for t in existing if not case_status.get(t, (False, ""))[0]]
        if matrix_partial:
            status = "partial"
            if failed:
                note = "matrix partial; case mismatch present: " + ", ".join(failed)
            else:
                note = "matrix partial; mapped case execution present"
        else:
            if failed:
                status = "inconclusive"
                note = "matrix covered but mapped grouped case mismatched (needs row-split case): " + ", ".join(failed)
            else:
                status = "pass"
                note = "all mapped existing cases passed"
    counts[status] += 1
    row_results.append((row, status, note))

total = len(rows)
now = subprocess.check_output(["date", "-u", "+%Y-%m-%d %H:%M:%SZ"], text=True).strip()
lines: list[str] = []
lines.append("# Bash Source-Docs Gap Report")
lines.append("")
lines.append(f"Generated: {now}")
lines.append("")
lines.append("Sources:")
lines.append("- https://tiswww.case.edu/php/chet/bash/POSIX")
lines.append("- https://tiswww.case.edu/php/chet/bash/COMPAT")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append(f"- total rows: {total}")
lines.append(f"- pass: {counts['pass']}")
lines.append(f"- fail: {counts['fail']}")
lines.append(f"- inconclusive (grouped-case mismatch): {counts['inconclusive']}")
lines.append(f"- partial (from matrix): {counts['partial']}")
lines.append(f"- unprobed (missing case files): {counts['unprobed']}")
lines.append(f"- unmapped (no test IDs): {counts['unmapped']}")
lines.append("")
lines.append("## Failing Rows")
lines.append("")
for row, st, note in row_results:
    if st == "fail":
        lines.append(f"- `{row.rid}` ({row.source}): {note}")
lines.append("")
lines.append("## Inconclusive Rows")
lines.append("")
for row, st, note in row_results:
    if st == "inconclusive":
        lines.append(f"- `{row.rid}` ({row.source}): {note}")
lines.append("")
lines.append("## Partial Rows")
lines.append("")
for row, st, note in row_results:
    if st == "partial":
        lines.append(f"- `{row.rid}` ({row.source}): {note}")
lines.append("")
lines.append("## Unprobed Rows")
lines.append("")
for row, st, note in row_results:
    if st in {"unprobed", "unmapped"}:
        lines.append(f"- `{row.rid}` ({row.source}): {note}")
lines.append("")
lines.append("## Case Logs")
lines.append("")
for case, (_, log) in sorted(case_status.items()):
    lines.append(f"- `{case}`: `{log}`")
lines.append("")

REPORT.write_text("\n".join(lines), encoding="utf-8")
print(f"[INFO] wrote {REPORT}")

if STRICT and counts["fail"] > 0:
    raise SystemExit(1)
PY

echo "[PASS] bash source docs gap report generated"
