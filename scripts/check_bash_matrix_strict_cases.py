#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> int:
    matrix_path = Path("docs/specs/bash-man-implementation-matrix.tsv")
    strict_map_path = Path("docs/specs/bash-man-strict-case-map.tsv")

    if not matrix_path.exists():
        print(f"[FAIL] missing {matrix_path}", file=sys.stderr)
        return 1
    if not strict_map_path.exists():
        print(f"[FAIL] missing {strict_map_path}", file=sys.stderr)
        return 1

    rows = read_tsv(matrix_path)
    strict_rows = read_tsv(strict_map_path)
    req_ids = {r["req_id"] for r in rows}
    by_req: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in strict_rows:
        by_req[r["req_id"]].append(r)

    missing = [rid for rid in sorted(req_ids) if rid not in by_req]
    stale = [rid for rid in sorted(by_req) if rid not in req_ids]
    invalid = []
    for rid, ents in by_req.items():
        for e in ents:
            sid = (e.get("strict_case_id") or "").strip()
            if not sid or sid.startswith("unmapped:"):
                invalid.append((rid, sid))

    if missing or stale or invalid:
        if missing:
            print("[FAIL] missing strict-case mappings:", file=sys.stderr)
            for rid in missing[:50]:
                print(f"  - {rid}", file=sys.stderr)
        if stale:
            print("[FAIL] stale strict-case mappings:", file=sys.stderr)
            for rid in stale[:50]:
                print(f"  - {rid}", file=sys.stderr)
        if invalid:
            print("[FAIL] invalid strict-case mappings:", file=sys.stderr)
            for rid, sid in invalid[:50]:
                print(f"  - {rid}: {sid}", file=sys.stderr)
        return 1

    total = len(req_ids)
    via_case = 0
    via_runner = 0
    for rid in req_ids:
        sids = [(e.get("strict_case_id") or "").strip() for e in by_req[rid]]
        if any(s.startswith("case:") for s in sids):
            via_case += 1
        elif any(s.startswith("runner:") for s in sids):
            via_runner += 1

    print("[PASS] bash matrix strict-case mapping")
    print(f"  total req rows: {total}")
    print(f"  mapped via case scripts: {via_case}")
    print(f"  mapped via strict runner rows: {via_runner}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

