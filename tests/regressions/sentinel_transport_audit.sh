#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET="$ROOT/src/mctash/runtime.py"

python3 - "$TARGET" <<'PY'
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")

structured_names = {
    "_expand_asdl_word_fields",
    "_asdl_word_to_expansion_fields",
    "_asdl_literal_to_segments",
    "_split_structured_field",
    "_chars_to_structured_field",
    "_glob_structured_field",
    "_expand_asdl_assignment_fields",
}
current = None
violations = []
for idx, line in enumerate(text.splitlines(), start=1):
    m = re.match(r"\s*def\s+([A-Za-z0-9_]+)\s*\(", line)
    if m:
        current = m.group(1)
    if "\\ue00" not in line:
        continue
    if current is None:
        continue
    if current.startswith("_asdl_") or current in structured_names:
        violations.append((idx, current, line.strip()))

if violations:
    print("[FAIL] sentinel_transport_audit: sentinel marker found in structured/ASDL path", file=sys.stderr)
    for ln, fn, src in violations:
        print(f"  {p}:{ln} ({fn}): {src}", file=sys.stderr)
    raise SystemExit(1)

print("[PASS] sentinel_transport_audit")
PY
