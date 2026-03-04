#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MATRIX="${ROOT}/tests/compat/semantic_matrix.tsv"
REPORT="${ROOT}/docs/reports/semantic-matrix-latest.md"
UPSTREAM_TROOT="${ROOT}/tests/bash/upstream/baserock-bash-5.1-testing/tests"
ROW_TIMEOUT_SIMPLE="${ROW_TIMEOUT_SIMPLE:-15}"
ROW_TIMEOUT_UPSTREAM="${ROW_TIMEOUT_UPSTREAM:-20}"
MCTASH_MAX_VMEM_KB="${MCTASH_MAX_VMEM_KB:-786432}"
ROW_FILTER="${ROW_FILTER:-}"
RUN_UPSTREAM_ROWS="${RUN_UPSTREAM_ROWS:-0}"

if [[ ! -f "$MATRIX" ]]; then
  echo "missing matrix: $MATRIX" >&2
  exit 2
fi

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

summary="$tmpdir/summary.tsv"
: >"$summary"

mk_wrapper() {
  local path="$1"
  local body="$2"
  cat >"$path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
${body}
EOF
  chmod +x "$path"
}

# Shared wrappers so simple-row scripts can call `${THIS_SH}` recursively.
w_ash="$tmpdir/w-ash.sh"
w_bp="$tmpdir/w-bash-posix.sh"
w_bf="$tmpdir/w-bash-full.sh"
w_mp="$tmpdir/w-mctash-posix.sh"
w_mb="$tmpdir/w-mctash-bash.sh"
mk_wrapper "$w_ash" "exec ash \"\$@\""
mk_wrapper "$w_bp" "exec bash --posix \"\$@\""
mk_wrapper "$w_bf" "exec bash \"\$@\""
mk_wrapper "$w_mp" "exec env PYTHONPATH=\"$ROOT/src\" MCTASH_MODE=posix MCTASH_MAX_VMEM_KB=\"$MCTASH_MAX_VMEM_KB\" python3 -m mctash --posix \"\$@\""
mk_wrapper "$w_mb" "exec env PYTHONPATH=\"$ROOT/src\" MCTASH_MODE=bash MCTASH_MAX_VMEM_KB=\"$MCTASH_MAX_VMEM_KB\" python3 -m mctash \"\$@\""

run_simple_row() {
  local script_file="$1"
  local ash_out="$2" ash_err="$3" ash_rc_var="$4"
  local bp_out="$5" bp_err="$6" bp_rc_var="$7"
  local bf_out="$8" bf_err="$9" bf_rc_var="${10}"
  local mp_out="${11}" mp_err="${12}" mp_rc_var="${13}"
  local mb_out="${14}" mb_err="${15}" mb_rc_var="${16}"

  local ash_rc=0 bp_rc=0 bf_rc=0 mp_rc=0 mb_rc=0
  set +e
  timeout -k 5 "$ROW_TIMEOUT_SIMPLE" env THIS_SH="$w_ash" ash "$script_file" >"$ash_out" 2>"$ash_err"; ash_rc=$?
  timeout -k 5 "$ROW_TIMEOUT_SIMPLE" env THIS_SH="$w_bp" bash --posix "$script_file" >"$bp_out" 2>"$bp_err"; bp_rc=$?
  timeout -k 5 "$ROW_TIMEOUT_SIMPLE" env THIS_SH="$w_bf" bash "$script_file" >"$bf_out" 2>"$bf_err"; bf_rc=$?
  timeout -k 5 "$ROW_TIMEOUT_SIMPLE" env THIS_SH="$w_mp" PYTHONPATH="$ROOT/src" MCTASH_MODE=posix MCTASH_MAX_VMEM_KB="$MCTASH_MAX_VMEM_KB" python3 -m mctash --posix "$script_file" >"$mp_out" 2>"$mp_err"; mp_rc=$?
  timeout -k 5 "$ROW_TIMEOUT_SIMPLE" env THIS_SH="$w_mb" PYTHONPATH="$ROOT/src" MCTASH_MODE=bash MCTASH_MAX_VMEM_KB="$MCTASH_MAX_VMEM_KB" python3 -m mctash "$script_file" >"$mb_out" 2>"$mb_err"; mb_rc=$?
  set -e

  printf -v "$ash_rc_var" '%s' "$ash_rc"
  printf -v "$bp_rc_var" '%s' "$bp_rc"
  printf -v "$bf_rc_var" '%s' "$bf_rc"
  printf -v "$mp_rc_var" '%s' "$mp_rc"
  printf -v "$mb_rc_var" '%s' "$mb_rc"
}

run_upstream_row() {
  local mode="$1"
  local case_name="$2"
  local ash_out="$3" ash_err="$4" ash_rc_var="$5"
  local bp_out="$6" bp_err="$7" bp_rc_var="$8"
  local bf_out="$9" bf_err="${10}" bf_rc_var="${11}"
  local mp_out="${12}" mp_err="${13}" mp_rc_var="${14}"
  local mb_out="${15}" mb_err="${16}" mb_rc_var="${17}"

  if [[ ! -d "$UPSTREAM_TROOT" ]]; then
    echo "missing upstream corpus at $UPSTREAM_TROOT" >&2
    exit 2
  fi
  if [[ ! -f "$UPSTREAM_TROOT/$case_name" ]]; then
    echo "missing upstream case: $UPSTREAM_TROOT/$case_name" >&2
    exit 2
  fi

  local ash_rc=0 bp_rc=0 bf_rc=0 mp_rc=0 mb_rc=0
  set +e
  ( cd "$UPSTREAM_TROOT" && timeout -k 5 "$ROW_TIMEOUT_UPSTREAM" env THIS_SH="$w_ash" ash "./$case_name" >"$ash_out" 2>"$ash_err" ); ash_rc=$?
  ( cd "$UPSTREAM_TROOT" && timeout -k 5 "$ROW_TIMEOUT_UPSTREAM" env THIS_SH="$w_bp" bash --posix "./$case_name" >"$bp_out" 2>"$bp_err" ); bp_rc=$?
  ( cd "$UPSTREAM_TROOT" && timeout -k 5 "$ROW_TIMEOUT_UPSTREAM" env THIS_SH="$w_mp" PYTHONPATH="$ROOT/src" MCTASH_MODE=posix MCTASH_MAX_VMEM_KB="$MCTASH_MAX_VMEM_KB" python3 -m mctash --posix "./$case_name" >"$mp_out" 2>"$mp_err" ); mp_rc=$?
  if [[ "$mode" == "full" ]]; then
    ( cd "$UPSTREAM_TROOT" && timeout -k 5 "$ROW_TIMEOUT_UPSTREAM" env THIS_SH="$w_bf" bash "./$case_name" >"$bf_out" 2>"$bf_err" ); bf_rc=$?
    ( cd "$UPSTREAM_TROOT" && timeout -k 5 "$ROW_TIMEOUT_UPSTREAM" env THIS_SH="$w_mb" PYTHONPATH="$ROOT/src" MCTASH_MODE=bash MCTASH_MAX_VMEM_KB="$MCTASH_MAX_VMEM_KB" python3 -m mctash "./$case_name" >"$mb_out" 2>"$mb_err" ); mb_rc=$?
  else
    : >"$bf_out"
    : >"$bf_err"
    : >"$mb_out"
    : >"$mb_err"
    bf_rc=-1
    mb_rc=-1
  fi
  set -e

  printf -v "$ash_rc_var" '%s' "$ash_rc"
  printf -v "$bp_rc_var" '%s' "$bp_rc"
  printf -v "$bf_rc_var" '%s' "$bf_rc"
  printf -v "$mp_rc_var" '%s' "$mp_rc"
  printf -v "$mb_rc_var" '%s' "$mb_rc"
}

row_idx=0
while IFS=$'\t' read -r id class spec script; do
  [[ -z "${id:-}" ]] && continue
  [[ "${id:0:1}" == "#" ]] && continue
  if [[ -n "$ROW_FILTER" ]] && [[ "$id" != $ROW_FILTER ]]; then
    continue
  fi
  row_idx=$((row_idx + 1))

  # Comparator/baseline executions
  ash_out="$tmpdir/${row_idx}-${id}.ash.out"; ash_err="$tmpdir/${row_idx}-${id}.ash.err"; ash_rc=0
  bp_out="$tmpdir/${row_idx}-${id}.bash_posix.out"; bp_err="$tmpdir/${row_idx}-${id}.bash_posix.err"; bp_rc=0
  bf_out="$tmpdir/${row_idx}-${id}.bash_full.out"; bf_err="$tmpdir/${row_idx}-${id}.bash_full.err"; bf_rc=0
  mp_out="$tmpdir/${row_idx}-${id}.mctash_posix.out"; mp_err="$tmpdir/${row_idx}-${id}.mctash_posix.err"; mp_rc=0
  mb_out="$tmpdir/${row_idx}-${id}.mctash_bash.out"; mb_err="$tmpdir/${row_idx}-${id}.mctash_bash.err"; mb_rc=0

  if [[ "$script" == @upstream:* ]]; then
    if [[ "$RUN_UPSTREAM_ROWS" != "1" ]]; then
      ash_rc=-1; bp_rc=-1; bf_rc=-1; mp_rc=-1; mb_rc=-1
      : >"$ash_out"; : >"$ash_err"; : >"$bp_out"; : >"$bp_err"; : >"$bf_out"; : >"$bf_err"; : >"$mp_out"; : >"$mp_err"; : >"$mb_out"; : >"$mb_err"
      posix_refs_agree=0
      mctash_posix_ok=0
      mctash_bash_ok=0
      row_status="info"
      row_note="upstream row skipped (set RUN_UPSTREAM_ROWS=1 to execute)"
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$id" "$class" "$spec" \
        "$ash_rc" "$bp_rc" "$bf_rc" "$mp_rc" "$mb_rc" \
        "$posix_refs_agree" "$mctash_posix_ok" "$mctash_bash_ok" \
        "$row_status" "$row_note" >>"$summary"
      continue
    fi
    case_name="${script#@upstream:}"
    upstream_mode="full"
    if [[ "$class" == "posix-required" ]]; then
      upstream_mode="posix-only"
    fi
    run_upstream_row "$upstream_mode" "$case_name" \
      "$ash_out" "$ash_err" ash_rc \
      "$bp_out" "$bp_err" bp_rc \
      "$bf_out" "$bf_err" bf_rc \
      "$mp_out" "$mp_err" mp_rc \
      "$mb_out" "$mb_err" mb_rc
  else
    script_file="$tmpdir/${row_idx}-${id}.sh"
    printf '%s\n' "$script" >"$script_file"
    run_simple_row "$script_file" \
      "$ash_out" "$ash_err" ash_rc \
      "$bp_out" "$bp_err" bp_rc \
      "$bf_out" "$bf_err" bf_rc \
      "$mp_out" "$mp_err" mp_rc \
      "$mb_out" "$mb_err" mb_rc
  fi

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

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$class" "$spec" \
    "$ash_rc" "$bp_rc" "$bf_rc" "$mp_rc" "$mb_rc" \
    "$posix_refs_agree" "$mctash_posix_ok" "$mctash_bash_ok" \
    "$row_status" "$row_note" >>"$summary"
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
