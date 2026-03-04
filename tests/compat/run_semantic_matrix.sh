#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MATRIX="${ROOT}/tests/compat/semantic_matrix.tsv"
REPORT="${ROOT}/docs/reports/semantic-matrix-latest.md"

if [[ ! -f "$MATRIX" ]]; then
  echo "missing matrix: $MATRIX" >&2
  exit 2
fi

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

summary="$tmpdir/summary.tsv"
: >"$summary"

row_idx=0
while IFS=$'\t' read -r id class spec script; do
  [[ -z "${id:-}" ]] && continue
  [[ "${id:0:1}" == "#" ]] && continue
  row_idx=$((row_idx + 1))
  script_file="$tmpdir/${row_idx}-${id}.sh"
  printf '%s\n' "$script" >"$script_file"

  # Comparator/baseline executions
  ash_out="$tmpdir/${row_idx}-${id}.ash.out"; ash_err="$tmpdir/${row_idx}-${id}.ash.err"; ash_rc=0
  bp_out="$tmpdir/${row_idx}-${id}.bash_posix.out"; bp_err="$tmpdir/${row_idx}-${id}.bash_posix.err"; bp_rc=0
  bf_out="$tmpdir/${row_idx}-${id}.bash_full.out"; bf_err="$tmpdir/${row_idx}-${id}.bash_full.err"; bf_rc=0
  mp_out="$tmpdir/${row_idx}-${id}.mctash_posix.out"; mp_err="$tmpdir/${row_idx}-${id}.mctash_posix.err"; mp_rc=0
  mb_out="$tmpdir/${row_idx}-${id}.mctash_bash.out"; mb_err="$tmpdir/${row_idx}-${id}.mctash_bash.err"; mb_rc=0

  set +e
  timeout -k 5 15 ash "$script_file" >"$ash_out" 2>"$ash_err"; ash_rc=$?
  timeout -k 5 15 bash --posix "$script_file" >"$bp_out" 2>"$bp_err"; bp_rc=$?
  timeout -k 5 15 bash "$script_file" >"$bf_out" 2>"$bf_err"; bf_rc=$?
  timeout -k 5 15 env PYTHONPATH="$ROOT/src" MCTASH_MODE=posix MCTASH_MAX_VMEM_KB=786432 python3 -m mctash --posix "$script_file" >"$mp_out" 2>"$mp_err"; mp_rc=$?
  timeout -k 5 15 env PYTHONPATH="$ROOT/src" MCTASH_MODE=bash MCTASH_MAX_VMEM_KB=786432 python3 -m mctash "$script_file" >"$mb_out" 2>"$mb_err"; mb_rc=$?
  set -e

  posix_refs_agree=0
  mctash_posix_ok=0
  mctash_bash_ok=0
  row_status="info"
  row_note=""

  if [[ "$ash_rc" -eq "$bp_rc" ]] && cmp -s "$ash_out" "$bp_out" && cmp -s "$ash_err" "$bp_err"; then
    posix_refs_agree=1
  fi
  if [[ "$mp_rc" -eq "$bp_rc" ]] && cmp -s "$mp_out" "$bp_out" && cmp -s "$mp_err" "$bp_err"; then
    mctash_posix_ok=1
  fi
  if [[ "$mb_rc" -eq "$bf_rc" ]] && cmp -s "$mb_out" "$bf_out" && cmp -s "$mb_err" "$bf_err"; then
    mctash_bash_ok=1
  fi

  case "$class" in
    posix-required)
      if [[ "$posix_refs_agree" -ne 1 ]]; then
        row_status="conflict"
        row_note="ash vs bash --posix differ"
      elif [[ "$mctash_posix_ok" -ne 1 ]]; then
        row_status="fail"
        row_note="mctash --posix diverges from POSIX baselines"
      else
        row_status="pass"
      fi
      ;;
    extension-bash)
      if [[ "$mctash_bash_ok" -ne 1 ]]; then
        row_status="fail"
        row_note="mctash bash-mode diverges from bash"
      else
        row_status="pass"
      fi
      ;;
    extension-ash)
      if [[ "$mp_rc" -eq "$ash_rc" ]] && cmp -s "$mp_out" "$ash_out" && cmp -s "$mp_err" "$ash_err"; then
        row_status="pass"
      else
        row_status="fail"
        row_note="mctash --posix diverges from ash extension behavior"
      fi
      ;;
    posix-unspecified|*)
      row_status="info"
      row_note="unspecified/extension behavior"
      ;;
  esac

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$class" "$spec" \
    "$ash_rc" "$bp_rc" "$bf_rc" "$mp_rc" "$mb_rc" \
    "$posix_refs_agree" "$mctash_posix_ok" "$mctash_bash_ok" \
    "$row_status" "$row_note" \
    "$ash_out" "$bp_out" >>"$summary"
done <"$MATRIX"

python3 - "$summary" "$REPORT" <<'PY'
import datetime
import sys
from pathlib import Path

summary = Path(sys.argv[1])
report = Path(sys.argv[2])
rows = []
for ln in summary.read_text().splitlines():
    parts = ln.split("\t")
    if len(parts) < 13:
        continue
    rows.append(parts)

def c(pred):
    return sum(1 for r in rows if pred(r))

now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
lines = [
    "# Semantic Matrix Report",
    "",
    f"Generated: {now}",
    "",
    "Matrix source: `tests/compat/semantic_matrix.tsv`",
    "",
    "## Summary",
    "",
    f"- total rows: {len(rows)}",
    f"- pass: {c(lambda r: r[11] == 'pass')}",
    f"- fail: {c(lambda r: r[11] == 'fail')}",
    f"- conflict: {c(lambda r: r[11] == 'conflict')}",
    f"- info: {c(lambda r: r[11] == 'info')}",
    "",
    "## Rows",
    "",
    "| id | class | spec | ash rc | bash --posix rc | bash rc | mctash --posix rc | mctash rc | posix refs agree | mctash-posix ok | mctash-bash ok | status | note |",
    "|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|",
]
for r in rows:
    lines.append(
        f"| `{r[0]}` | {r[1]} | `{r[2]}` | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {('yes' if r[8]=='1' else 'no')} | {('yes' if r[9]=='1' else 'no')} | {('yes' if r[10]=='1' else 'no')} | {r[11]} | {r[12] or '-'} |"
    )

lines += [
    "",
    "## Policy",
    "",
    "- `posix-required`: ash and `bash --posix` must agree, and `mctash --posix` must match.",
    "- `extension-bash`: `mctash` default mode must match bash default mode.",
    "- `extension-ash`: `mctash --posix` must match ash for ash-specific behavior.",
    "- `posix-unspecified`: tracked informationally until policy is pinned.",
]

report.write_text("\n".join(lines) + "\n")
print(report)
PY

if awk -F'\t' '($12=="fail" || $12=="conflict") {exit 1}' "$summary"; then
  echo "[PASS] semantic matrix"
else
  echo "[FAIL] semantic matrix" >&2
  exit 1
fi
