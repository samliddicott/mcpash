#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASES_DIR="${ROOT}/tests/diff/cases"
LOG_ROOT="${ROOT}/tests/diff/logs/matrix"
REPORT="${ROOT}/docs/reports/bash-gap-latest.md"
PARITY_COMPAT="${PARITY_COMPAT:-50}"

mkdir -p "${LOG_ROOT}"

mapfile -t CASE_FILES < <(cd "${CASES_DIR}" && ls *.sh 2>/dev/null | sort)

ash_cases=()
bash_cases=()
for c in "${CASE_FILES[@]}"; do
  p="${CASES_DIR}/${c}"
  if grep -q '^# DIFF_BASELINE: bash$' "$p"; then
    bash_cases+=("${c%.sh}")
  else
    ash_cases+=("${c%.sh}")
  fi
done

run_lane() {
  local lane="$1"
  shift
  local out="${LOG_ROOT}/${lane}.out"
  local rc=0
  set +e
  "$@" >"$out" 2>&1
  rc=$?
  set -e
  echo "$rc"
}

ash_rc=0
bash_rc=0
if [[ ${#ash_cases[@]} -gt 0 ]]; then
  ash_rc=$(run_lane ash tests/diff/run.sh --logdir "${LOG_ROOT}/ash" "${ash_cases[@]}")
fi
if [[ ${#bash_cases[@]} -gt 0 ]]; then
  bash_rc=$(run_lane bash env PARITY_BASH_COMPAT="${PARITY_COMPAT}" PARITY_MIRROR_POSIX=1 MCTASH_MODE_DEFAULT=posix tests/diff/run.sh --logdir "${LOG_ROOT}/bash" "${bash_cases[@]}")
fi

ash_fail_lines="${LOG_ROOT}/ash.fail.lines"
bash_fail_lines="${LOG_ROOT}/bash.fail.lines"
grep -E '(^[^[:space:]]+: (stdout|stderr|exit status) mismatch)' "${LOG_ROOT}/ash.out" >"${ash_fail_lines}" || true
grep -E '(^[^[:space:]]+: (stdout|stderr|exit status) mismatch)' "${LOG_ROOT}/bash.out" >"${bash_fail_lines}" || true

ash_fail_count=$(wc -l <"${ash_fail_lines}" | tr -d ' ')
bash_fail_count=$(wc -l <"${bash_fail_lines}" | tr -d ' ')

now="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
{
  echo "# Bash Gap Report"
  echo
  echo "Generated: ${now}"
  echo "BASH_COMPAT: ${PARITY_COMPAT}"
  echo
  echo "## Summary"
  echo
  echo "- ash lane cases: ${#ash_cases[@]} (rc=${ash_rc}, mismatches=${ash_fail_count})"
  echo "- bash lane cases: ${#bash_cases[@]} (rc=${bash_rc}, mismatches=${bash_fail_count})"
  echo
  echo "## Bash Lane Mismatches"
  echo
  if [[ "${bash_fail_count}" -eq 0 ]]; then
    echo "- none"
  else
    sed 's/^/- /' "${bash_fail_lines}"
  fi
  echo
  echo "## Ash Lane Mismatches"
  echo
  if [[ "${ash_fail_count}" -eq 0 ]]; then
    echo "- none"
  else
    sed 's/^/- /' "${ash_fail_lines}"
  fi
} >"${REPORT}"

echo "[INFO] wrote ${REPORT}"
echo "[INFO] ash lane rc=${ash_rc} mismatches=${ash_fail_count}"
echo "[INFO] bash lane rc=${bash_rc} mismatches=${bash_fail_count}"

if [[ "${bash_rc}" -ne 0 || "${ash_rc}" -ne 0 ]]; then
  exit 1
fi
