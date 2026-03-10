#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="${ROOT}/docs/reports/busybox-timeout-reproducer-latest.md"
LOG="${BUSYBOX_SCAN_LOG:-/tmp/busybox-timeout-repro.log}"

# Keep this bounded for routine triage runs.
RUN_TIMEOUT="${RUN_TIMEOUT:-25}"
RUN_MODULE_TIMEOUT="${RUN_MODULE_TIMEOUT:-25}"
BUSYBOX_FAIL_FAST_ON_TIMEOUT="${BUSYBOX_FAIL_FAST_ON_TIMEOUT:-1}"

mapfile -t mods < <(find "${ROOT}/tests/busybox/ash_test" -mindepth 1 -maxdepth 1 -type d -name 'ash-*' -printf '%f\n' | sort)

: > "${LOG}"
for m in "${mods[@]}"; do
  echo "=== ${m} ===" >>"${LOG}"
  set +e
  RUN_TIMEOUT="${RUN_TIMEOUT}" \
  RUN_MODULE_TIMEOUT="${RUN_MODULE_TIMEOUT}" \
  BUSYBOX_FAIL_FAST_ON_TIMEOUT="${BUSYBOX_FAIL_FAST_ON_TIMEOUT}" \
    "${ROOT}/src/tests/run_busybox_ash.sh" run "${m}" >>"${LOG}" 2>&1
  rc=$?
  set -e
  echo "rc=${rc}" >>"${LOG}"
  echo >>"${LOG}"
done

python3 - <<'PY'
from pathlib import Path
import datetime
import os

log_path = Path(os.environ.get("BUSYBOX_SCAN_LOG", "/tmp/busybox-timeout-repro.log"))
lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
current = None
timeouts = []
nonzero = []
for line in lines:
    if line.startswith("=== "):
        current = line.split()[1]
    elif line.startswith("Timeout modules: "):
        detail = line.split(": ", 1)[1].strip()
        timeouts.append((current, detail))
    elif line.startswith("rc=") and line.strip() != "rc=0":
        nonzero.append((current, line.strip()))

out = []
out.append("# BusyBox Timeout Reproducer")
out.append("")
out.append(f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}")
out.append("")
out.append("## Reproducer Settings")
out.append("")
out.append("- Runner: `./src/tests/run_busybox_ash.sh run <module>`")
out.append(f"- `RUN_TIMEOUT={os.environ.get('RUN_TIMEOUT', '25')}`")
out.append(f"- `RUN_MODULE_TIMEOUT={os.environ.get('RUN_MODULE_TIMEOUT', '25')}`")
out.append(f"- `BUSYBOX_FAIL_FAST_ON_TIMEOUT={os.environ.get('BUSYBOX_FAIL_FAST_ON_TIMEOUT', '1')}`")
out.append("")
out.append("## Modules That Timed Out")
out.append("")
if timeouts:
    for mod, detail in timeouts:
        out.append(f"- `{mod}` -> {detail}")
else:
    out.append("- none")
out.append("")
out.append("## Modules With Non-zero Exit")
out.append("")
if nonzero:
    for mod, rc in nonzero:
        out.append(f"- `{mod}`: {rc}")
else:
    out.append("- none")
out.append("")
out.append("## Notes")
out.append("")
out.append("- This is a bounded reproducer for harness triage, not a full conformance run.")
out.append(f"- Full detailed run log: `{log_path}` (local temporary file).")
Path("docs/reports/busybox-timeout-reproducer-latest.md").write_text("\n".join(out) + "\n", encoding="utf-8")
PY

echo "Wrote ${REPORT}"
echo "Log ${LOG}"
