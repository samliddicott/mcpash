#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/specs/bash-man-implementation-matrix.tsv"
STRICT_MAP = ROOT / "docs/specs/bash-man-strict-case-map.tsv"
INVOCATION_RUNNER = ROOT / "tests/compat/run_bash_invocation_option_matrix.sh"
MAN_MATRIX_RUNNER = ROOT / "tests/compat/run_bash_posix_man_matrix.sh"


def _load_matrix_rows() -> list[dict[str, str]]:
    with MATRIX.open(newline="", encoding="utf-8", errors="surrogateescape") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _load_strict_rows() -> list[dict[str, str]]:
    with STRICT_MAP.open(newline="", encoding="utf-8", errors="surrogateescape") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _fail(msg: str) -> int:
    print(f"[FAIL] {msg}")
    return 1


def check(req_id: str) -> int:
    rows = _load_matrix_rows()
    by_req = {r["req_id"]: r for r in rows}
    if req_id not in by_req:
        return _fail(f"missing req row: {req_id}")
    row = by_req[req_id]
    text_inv = INVOCATION_RUNNER.read_text(encoding="utf-8", errors="surrogateescape")
    text_man = MAN_MATRIX_RUNNER.read_text(encoding="utf-8", errors="surrogateescape")

    if req_id == "C12.MATRIX.01":
        # bash default comparator lane should exist.
        if " bash)" not in text_inv and "cmd=(bash)" not in text_inv:
            return _fail("missing bash default comparator lane in invocation matrix")
        print("[PASS] C12.MATRIX.01")
        return 0

    if req_id == "C12.MATRIX.02":
        # bash --posix comparator lane should exist.
        if "BASH_BIN='bash --posix'" not in text_man:
            return _fail("missing bash --posix comparator lane in man matrix runner")
        print("[PASS] C12.MATRIX.02")
        return 0

    if req_id == "C12.MATRIX.03":
        if "mctash_default" not in row:
            return _fail("matrix missing mctash_default column")
        print("[PASS] C12.MATRIX.03")
        return 0

    if req_id == "C12.MATRIX.04":
        if "mctash_posix" not in row:
            return _fail("matrix missing mctash_posix column")
        print("[PASS] C12.MATRIX.04")
        return 0

    if req_id == "C12.MATRIX.05":
        strict_rows = _load_strict_rows()
        mapped = {r["req_id"] for r in strict_rows if (r.get("strict_case_id") or "").strip()}
        if not all(r["req_id"] in mapped for r in rows):
            return _fail("not all matrix rows have strict-case mapping")
        print("[PASS] C12.MATRIX.05")
        return 0

    if req_id == "C12.MATRIX.06":
        missing = [r["req_id"] for r in rows if not (r.get("posix_mode_status") or "").strip()]
        if missing:
            return _fail(f"rows missing posix_mode_status: {', '.join(missing[:5])}")
        print("[PASS] C12.MATRIX.06")
        return 0

    if req_id == "C12.MATRIX.07":
        bad: list[str] = []
        # Guard against shorthand wording ("etc", "..."), but do not flag
        # literal filesystem paths like "/etc/profile".
        bad_re = re.compile(r"(?<!/)\betc\b|\.{3}", re.IGNORECASE)
        for r in rows:
            if bad_re.search(r.get("feature", "")) or bad_re.search(r.get("notes", "")):
                bad.append(r["req_id"])
        if bad:
            return _fail(f"rows use grouped shorthand etc/ellipsis: {', '.join(bad[:5])}")
        print("[PASS] C12.MATRIX.07")
        return 0

    return _fail(f"unsupported req id: {req_id}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--req", required=True, help="req id, e.g. C12.MATRIX.01")
    ns = ap.parse_args()
    return check(ns.req.strip())


if __name__ == "__main__":
    raise SystemExit(main())
