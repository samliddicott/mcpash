#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQ_TSV = ROOT / "docs/specs/bash-man-requirements.tsv"
MATRIX_TSV = ROOT / "docs/specs/bash-man-implementation-matrix.tsv"
JOB_DESIGN_REF = "design:docs/design/job-control-runtime-model.md"
JOB_ROW_RE = re.compile(r"^C8\.JOB\.(1[4-9]|2[0-9])$")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> int:
    req_rows = load_rows(REQ_TSV)
    matrix_rows = load_rows(MATRIX_TSV)

    req_ids = [r.get("req_id", "").strip() for r in req_rows if r.get("req_id", "").strip()]
    matrix_ids = [r.get("req_id", "").strip() for r in matrix_rows if r.get("req_id", "").strip()]

    req_set = set(req_ids)
    matrix_set = set(matrix_ids)
    errors: list[str] = []

    missing = sorted(req_set - matrix_set)
    if missing:
        errors.append(f"Missing matrix rows for requirements: {', '.join(missing)}")

    extra = sorted(matrix_set - req_set)
    if extra:
        errors.append(f"Matrix rows without requirements: {', '.join(extra)}")

    for row in matrix_rows:
        req_id = row.get("req_id", "").strip()
        status_default = row.get("mctash_default", "").strip()
        status_posix = row.get("mctash_posix", "").strip()
        tests = row.get("tests", "").strip()
        notes = row.get("notes", "").strip()

        if status_default in {"covered", "partial"} or status_posix in {"covered", "partial"}:
            if not tests:
                errors.append(f"{req_id}: covered/partial row must include test ids")

        if JOB_ROW_RE.match(req_id):
            if JOB_DESIGN_REF not in notes:
                errors.append(f"{req_id}: missing design linkage note '{JOB_DESIGN_REF}'")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}", file=sys.stderr)
        return 1

    print("[PASS] spec cycle check")
    print(f"- requirements rows: {len(req_rows)}")
    print(f"- matrix rows: {len(matrix_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
