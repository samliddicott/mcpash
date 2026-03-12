#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TROOT="${ROOT}/tests/bash/upstream/baserock-bash-5.1-testing/tests"
RDIR="${ROOT}/tests/bash/upstream/baserock-bash-5.1-testing/run-default"
REPORT="${ROOT}/docs/reports/bash-default-upstream-gap-latest.md"

if [[ ! -d "$TROOT" ]]; then
  echo "missing upstream corpus at $TROOT" >&2
  echo "fetch/populate first" >&2
  exit 2
fi

mkdir -p "$RDIR/bash" "$RDIR/mctash" "$RDIR/diff"

normalize_for_diff() {
  local src="$1"
  local dst="$2"
  python3 - "$src" "$dst" <<'PY'
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
text = src.read_text(errors="replace")
text = re.sub(r"/(extglob|eglob-test|bash-globignore)-[0-9]+", r"/\1-<PID>", text)

out_lines = []
for line in text.splitlines():
    m = re.match(r"^(declare -A[i]?\s+[A-Za-z_][A-Za-z0-9_]*=\()(.*)(\)\s*)$", line)
    if not m:
        out_lines.append(line)
        continue
    body = m.group(2)
    pairs = re.findall(r"\[[^]]+\]=\"(?:[^\"\\\\]|\\\\.)*\"", body)
    if not pairs:
        out_lines.append(line)
        continue
    out_lines.append(m.group(1) + " ".join(sorted(pairs)) + " " + m.group(3).rstrip())

dst.write_text("\n".join(out_lines) + ("\n" if text.endswith("\n") else ""))
PY
}

cat > "$RDIR/bash_wrapper.sh" <<'W1'
#!/usr/bin/env bash
exec bash "$@"
W1
chmod +x "$RDIR/bash_wrapper.sh"

cat > "$RDIR/mctash_wrapper.sh" <<'W2'
#!/usr/bin/env bash
exec env PYTHONPATH=/home/sam/Projects/pybash/src MCTASH_MODE=bash MCTASH_DIAG_STYLE=bash BASH_COMPAT=50 python3 -m mctash "$@"
W2
chmod +x "$RDIR/mctash_wrapper.sh"

run_case_isolated() {
  local shell_kind="$1"   # bash|mctash
  local case_name="$2"
  local out_file="$3"
  local err_file="$4"
  local case_timeout="$5"
  local rc=0
  local run_root
  run_root="$(mktemp -d "${RDIR}/isolation.${shell_kind}.${case_name}.XXXXXX")"
  local run_home="${run_root}/home"
  local run_tmp="${run_root}/tmp"
  mkdir -p "$run_home" "$run_tmp"

  local path_safe="${PATH:-/usr/bin:/bin}"
  local -a base_env=(
    "HOME=$run_home"
    "TMPDIR=$run_tmp"
    "PARENT=$run_tmp"
    "XDG_CACHE_HOME=$run_home/.cache"
    "XDG_CONFIG_HOME=$run_home/.config"
    "XDG_DATA_HOME=$run_home/.local/share"
    "HISTFILE=$run_home/.bash_history"
    "INPUTRC=/dev/null"
    "BASH_ENV=/dev/null"
    "ENV=/dev/null"
    "CDPATH="
    "GLOBIGNORE="
    "SHELLOPTS="
    "BASHOPTS="
    "LC_ALL=C"
    "LANG=C"
    "PATH=$path_safe"
    "BASH_COMPAT=50"
    "THIS_SH=$RDIR/${shell_kind}_wrapper.sh"
  )

  local cmd
  if [[ "$shell_kind" == "bash" ]]; then
    cmd=(
      env -i "${base_env[@]}" \
      timeout -k 5 "$case_timeout" \
      bash -lc "cd '$TROOT'; exec bash './$case_name'"
    )
  else
    cmd=(
      env -i "${base_env[@]}" \
      "PYTHONPATH=$ROOT/src" "MCTASH_MODE=bash" "MCTASH_DIAG_STYLE=bash" "MCTASH_MAX_VMEM_KB=786432" \
      timeout -k 5 "$case_timeout" \
      bash -lc "cd '$TROOT'; exec python3 -m mctash './$case_name'"
    )
  fi

  # Run each case in its own session. On timeout/interrupt, kill the whole process group.
  setsid "${cmd[@]}" >"$out_file" 2>"$err_file" || rc=$?
  if [[ "$rc" -eq 124 || "$rc" -eq 137 || "$rc" -eq 143 ]]; then
    # Best effort cleanup for stragglers from this isolated run root.
    pkill -f "$run_root" >/dev/null 2>&1 || true
  fi
  rm -rf "$run_root"
  return "$rc"
}

core_cases=(
  alias.tests
  appendop.tests
  arith.tests
  array.tests
  assoc.tests
  builtins.tests
  case.tests
  comsub.tests
  cond.tests
  coproc.tests
  errors.tests
  exp.tests
  exportfunc.tests
  extglob.tests
)

if [[ -n "${BASH_DEFAULT_UPSTREAM_CASES:-}" ]]; then
  # Space-separated override for focused debugging.
  read -r -a core_cases <<<"${BASH_DEFAULT_UPSTREAM_CASES}"
fi

summary="$RDIR/summary.tsv"
: > "$summary"

for c in "${core_cases[@]}"; do
  case_timeout=90
  if [[ "$c" == "arith.tests" ]]; then
    # Arithmetic corpus executes thousands of arithmetic evaluations.
    # Keep a higher cap to avoid false timeout failures while we optimize.
    case_timeout=300
  fi
  b_out="$RDIR/bash/${c}.out"; b_err="$RDIR/bash/${c}.err"; b_rc=0
  m_out="$RDIR/mctash/${c}.out"; m_err="$RDIR/mctash/${c}.err"; m_rc=0
  run_case_isolated bash "$c" "$b_out" "$b_err" "$case_timeout" || b_rc=$?
  run_case_isolated mctash "$c" "$m_out" "$m_err" "$case_timeout" || m_rc=$?
  out_m=0
  err_m=0
  b_out_n="$RDIR/bash/${c}.out.norm"
  m_out_n="$RDIR/mctash/${c}.out.norm"
  b_err_n="$RDIR/bash/${c}.err.norm"
  m_err_n="$RDIR/mctash/${c}.err.norm"
  normalize_for_diff "$b_out" "$b_out_n"
  normalize_for_diff "$m_out" "$m_out_n"
  normalize_for_diff "$b_err" "$b_err_n"
  normalize_for_diff "$m_err" "$m_err_n"
  diff -u "$b_out_n" "$m_out_n" >"$RDIR/diff/${c}.out.diff" || out_m=1
  diff -u "$b_err_n" "$m_err_n" >"$RDIR/diff/${c}.err.diff" || err_m=1
  printf '%s\t%s\t%s\t%s\t%s\n' "$c" "$b_rc" "$m_rc" "$out_m" "$err_m" >>"$summary"
done

python3 - <<'PY'
from pathlib import Path
import datetime

root = Path('/home/sam/Projects/pybash')
rdir = root / 'tests/bash/upstream/baserock-bash-5.1-testing/run-default'
rows = []
for line in (rdir / 'summary.tsv').read_text().splitlines():
    c, b, m, o, e = line.split('\t')
    rows.append((c, int(b), int(m), int(o), int(e)))
full = sum(1 for r in rows if r[1] == r[2] and r[3] == 0 and r[4] == 0)
fail = len(rows) - full
report = root / 'docs/reports/bash-default-upstream-gap-latest.md'
now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
lines = [
    '# Bash Default Upstream Gap Report',
    '',
    f'Generated: {now}',
    'Comparator baseline: GNU bash default mode (baserock mirror corpus, `bash-5.1-testing`)',
    'Target: `mctash` default mode (`BASH_COMPAT=50`)',
    '',
    '## Summary',
    '',
    f'- core full parity: {full}/{len(rows)}',
    f'- core failing rows: {fail}',
    '',
    '## Case Results',
    '',
    '| Case | bash rc | mctash rc | stdout | stderr |',
    '|---|---:|---:|---|---|',
]
for c, b, m, o, e in rows:
    lines.append(f'| `{c}` | {b} | {m} | {"mismatch" if o else "ok"} | {"mismatch" if e else "ok"} |')
lines += [
    '',
    '## Artifacts',
    '',
    '- Per-case outputs: `tests/bash/upstream/baserock-bash-5.1-testing/run-default/bash/` and `tests/bash/upstream/baserock-bash-5.1-testing/run-default/mctash/`',
    '- Per-case diffs: `tests/bash/upstream/baserock-bash-5.1-testing/run-default/diff/`',
]
report.write_text('\n'.join(lines) + '\n')
print(report)
PY

if awk -F'\t' '($2 != $3 || $4 != 0 || $5 != 0) {exit 1}' "$summary"; then
  echo "[PASS] bash default upstream core lane"
else
  echo "[FAIL] bash default upstream core lane" >&2
  exit 1
fi
