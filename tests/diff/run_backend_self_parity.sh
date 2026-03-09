#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASES_DIR="${ROOT}/tests/diff/cases"
LOG_DIR="${ROOT}/tests/diff/logs/backend-self"
REPORT="${ROOT}/docs/reports/backend-self-parity-latest.md"
MCTASH_CMD="${MCTASH_CMD:-PYTHONPATH=${ROOT}/src python3 -m mctash}"
PARITY_MIRROR_POSIX="${PARITY_MIRROR_POSIX:-1}"
CASE_FILTER=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --case)
      CASE_FILTER+=("$2")
      shift 2
      ;;
    *)
      CASE_FILTER+=("$1")
      shift
      ;;
  esac
done

mapfile -t CASE_FILES < <(cd "${CASES_DIR}" && ls *.sh 2>/dev/null | sort)
if [[ ${#CASE_FILTER[@]} -gt 0 ]]; then
  filtered=()
  for f in "${CASE_FILTER[@]}"; do
    exact="${f%.sh}.sh"
    for c in "${CASE_FILES[@]}"; do [[ "$c" == "$exact" ]] && filtered+=("$c"); done
    if [[ ${#filtered[@]} -eq 0 ]]; then
      for c in "${CASE_FILES[@]}"; do [[ "$c" == *"$f"* ]] && filtered+=("$c"); done
    fi
  done
  mapfile -t CASE_FILES < <(printf '%s\n' "${filtered[@]}" | awk '!seen[$0]++')
fi

mkdir -p "${LOG_DIR}/interpreter" "${LOG_DIR}/compiled" "${LOG_DIR}/diff"
mismatch=0
ran=0

for case in "${CASE_FILES[@]}"; do
  name="${case%.sh}"
  i_out="${LOG_DIR}/interpreter/${name}.out"
  i_err="${LOG_DIR}/interpreter/${name}.err"
  c_out="${LOG_DIR}/compiled/${name}.out"
  c_err="${LOG_DIR}/compiled/${name}.err"
  d_file="${LOG_DIR}/diff/${name}.txt"

  mode="posix"
  opts=""
  if grep -q '^# DIFF_BASELINE: bash$' "${CASES_DIR}/${case}"; then
    mode="bash"
    if [[ "${PARITY_MIRROR_POSIX}" == "1" ]]; then
      opts="--posix "
    fi
  fi

  set +e
  eval "MCTASH_MODE=${mode} MCTASH_BACKEND=interpreter ${MCTASH_CMD} ${opts}\"${CASES_DIR}/${case}\"" >"${i_out}" 2>"${i_err}"
  i_rc=$?
  eval "MCTASH_MODE=${mode} MCTASH_BACKEND=compiled ${MCTASH_CMD} ${opts}\"${CASES_DIR}/${case}\"" >"${c_out}" 2>"${c_err}"
  c_rc=$?
  set -e

  ((ran+=1))
  case_mismatch=0
  {
    if [[ $i_rc -ne $c_rc ]]; then
      echo "status mismatch: interpreter=${i_rc} compiled=${c_rc}"
      case_mismatch=1
    fi
    if ! diff -u "${i_out}" "${c_out}" >/dev/null; then
      echo "stdout mismatch"
      diff -u "${i_out}" "${c_out}" || true
      case_mismatch=1
    fi
    if ! diff -u "${i_err}" "${c_err}" >/dev/null; then
      echo "stderr mismatch"
      diff -u "${i_err}" "${c_err}" || true
      case_mismatch=1
    fi
  } >"${d_file}"

  if [[ ${case_mismatch} -ne 0 ]]; then
    ((mismatch+=1))
  else
    : >"${d_file}"
  fi

done

{
  echo "# Backend Self-Parity"
  echo
  echo "Generated: $(date -u +'%Y-%m-%d %H:%M:%SZ')"
  echo
  echo "## Summary"
  echo
  echo "- cases run: ${ran}"
  echo "- mismatches: ${mismatch}"
  echo
  if [[ ${mismatch} -gt 0 ]]; then
    echo "## Mismatches"
    echo
    for case in "${CASE_FILES[@]}"; do
      name="${case%.sh}"
      d_file="${LOG_DIR}/diff/${name}.txt"
      if [[ -s "${d_file}" ]]; then
        echo "- ${name}"
      fi
    done
  fi
} >"${REPORT}"

echo "[INFO] wrote ${REPORT}"
if [[ ${mismatch} -gt 0 ]]; then
  echo "[FAIL] backend self-parity" >&2
  exit 1
fi

echo "[PASS] backend self-parity"
