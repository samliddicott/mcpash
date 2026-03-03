#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
src_root = root / "src" / "mctash"
allowed_sentinel_files = {
    src_root / "expand.py",
}

violations = []
for p in src_root.rglob("*.py"):
    text = p.read_text(encoding="utf-8")
    if "\\ue00" not in text:
        continue
    if p not in allowed_sentinel_files:
        for idx, line in enumerate(text.splitlines(), start=1):
            if "\\ue00" in line:
                violations.append((p, idx, line.strip()))

if violations:
    print("[FAIL] sentinel_transport_audit: sentinel marker found outside allowlisted files", file=sys.stderr)
    for p, ln, src in violations:
        print(f"  {p}:{ln}: {src}", file=sys.stderr)
    raise SystemExit(1)

print("[PASS] sentinel_transport_audit")
PY
