#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing report: {path}")
    return path.read_text(encoding="utf-8", errors="surrogateescape")


def _extract_int(pattern: str, text: str, label: str) -> int:
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        raise SystemExit(f"missing metric '{label}'")
    return int(m.group(1))


def main() -> int:
    upstream = _read(ROOT / "docs/reports/bash-posix-upstream-gap-latest.md")
    man = _read(ROOT / "docs/reports/bash-posix-man-matrix-latest.md")
    builtin = _read(ROOT / "docs/reports/bash-builtin-matrix-latest.md")
    remaining = _read(ROOT / "docs/reports/bash-compliance-remaining-work-latest.md")
    gaps = _read(ROOT / "docs/reports/bash-compliance-gaps-latest.md")
    matrix_path = ROOT / "docs/specs/bash-man-implementation-matrix.tsv"

    upstream_fail = _extract_int(r"core failing rows:\s*(\d+)", upstream, "upstream core failing rows")
    man_rc = _extract_int(r"matrix exit code:\s*(\d+)", man, "man matrix exit code")
    man_mismatch = _extract_int(r"mismatch lines detected:\s*(\d+)", man, "man matrix mismatch lines")
    builtin_rc = _extract_int(r"overall rc:\s*(\d+)", builtin, "builtin matrix overall rc")
    remaining_total = _extract_int(r"Total remaining items:\s*(\d+)", remaining, "remaining total")

    hard_fail = upstream_fail != 0 or man_rc != 0 or man_mismatch != 0 or builtin_rc != 0

    partial_rows = 0
    with matrix_path.open(encoding="utf-8", errors="surrogateescape") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row.get("mctash_default") == "partial" or row.get("mctash_posix") == "partial":
                partial_rows += 1

    if hard_fail and remaining_total == 0:
        raise SystemExit("inconsistent reports: failing gates but remaining-work says 0")
    if (not hard_fail) and partial_rows == 0 and remaining_total != 0:
        raise SystemExit("inconsistent reports: gates are green with no partial rows but remaining-work is non-zero")
    if partial_rows > 0 and remaining_total == 0:
        raise SystemExit("inconsistent reports: matrix has partial rows but remaining-work says 0")

    if not hard_fail and partial_rows == 0:
        if "None at current HEAD." not in gaps:
            raise SystemExit("inconsistent gap report: expected explicit no-gap statement")
    else:
        if "None at current HEAD." in gaps:
            raise SystemExit("inconsistent gap report: claims no gaps while gates fail")

    print("[PASS] compliance truth checker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
