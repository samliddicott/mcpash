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
  b_out="$RDIR/bash/${c}.out"; b_err="$RDIR/bash/${c}.err"; b_rc=0
  m_out="$RDIR/mctash/${c}.out"; m_err="$RDIR/mctash/${c}.err"; m_rc=0
  (
    cd "$TROOT" &&
      timeout -k 5 "$case_timeout" env BASH_COMPAT=50 THIS_SH="$RDIR/bash_wrapper.sh" bash "./$c" >"$b_out" 2>"$b_err"
  ) || b_rc=$?
  (
    cd "$TROOT" &&
      timeout -k 5 "$case_timeout" env BASH_COMPAT=50 THIS_SH="$RDIR/mctash_wrapper.sh" \
        PYTHONPATH="$ROOT/src" MCTASH_MODE=bash MCTASH_DIAG_STYLE=bash MCTASH_MAX_VMEM_KB=786432 \
        python3 -m mctash "./$c" >"$m_out" 2>"$m_err"
  ) || m_rc=$?
  out_m=0
  err_m=0
  diff -u "$b_out" "$m_out" >"$RDIR/diff/${c}.out.diff" || out_m=1
  diff -u "$b_err" "$m_err" >"$RDIR/diff/${c}.err.diff" || err_m=1
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
