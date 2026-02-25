#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASES_DIR="${ROOT}/tests/diff/cases"
LOG_DIR="${ROOT}/tests/diff/logs"
ASH_BIN="${ASH_BIN:-ash}"
read -r -a ASH_CMD <<< "${ASH_BIN}"
MCTASH_CMD="${MCTASH_CMD:-PYTHONPATH=${ROOT}/src python3 -m mctash}"

GENERATE_EXPECTED=0
CASE_FILTER=()
ASH_ONLY=0
MCTASH_ONLY=0

usage() {
  cat <<'USAGE'
Usage: run.sh [opts] [case.sh...]

Options:
  --generate          update expected outputs with ash results
  --logdir DIR        override base log directory (default tests/diff/logs)
  --ash-only          emit ash outputs only
  --mctash-only       emit mctash outputs only
  --case NAME         run cases whose name contains NAME
USAGE
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --generate)
        GENERATE_EXPECTED=1
        shift
        ;;
      --logdir)
        LOG_DIR="$2"
        shift 2
        ;;
      --ash-only)
        ASH_ONLY=1
        shift
        ;;
      --mctash-only)
        MCTASH_ONLY=1
        shift
        ;;
      --case)
        CASE_FILTER+=("$2")
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        CASE_FILTER+=("$1")
        shift
        ;;
    esac
  done
}

parse_args "$@"

if [[ ! -d "${CASES_DIR}" ]]; then
  echo "No case scripts under ${CASES_DIR}." >&2
  exit 1
fi

mapfile -t CASE_FILES < <(cd "${CASES_DIR}" && ls *.sh 2>/dev/null | sort)
if [[ ${#CASE_FILES[@]} -eq 0 ]]; then
  echo "No cases found in ${CASES_DIR}." >&2
  exit 1
fi

FILTERED=()
if [[ ${#CASE_FILTER[@]} -gt 0 ]]; then
  for case in "${CASE_FILES[@]}"; do
    for filter in "${CASE_FILTER[@]}"; do
      [[ "${case}" == *"${filter}"* ]] && FILTERED+=("${case}") && break
    done
  done
  CASE_FILES=("${FILTERED[@]}")
fi

if [[ ${ASH_ONLY} -eq 1 && ${MCTASH_ONLY} -eq 1 ]]; then
  echo "Cannot use --ash-only and --mctash-only together." >&2
  exit 1
fi

mkdir -p "${LOG_DIR}/ash" "${LOG_DIR}/mctash" "${LOG_DIR}/diff" "${LOG_DIR}/expected"
RESULT=0

for case in "${CASE_FILES[@]}"; do
  name="${case%.sh}"
  ash_stdout="${LOG_DIR}/ash/${name}.out"
  ash_stderr="${LOG_DIR}/ash/${name}.err"
  mctash_stdout="${LOG_DIR}/mctash/${name}.out"
  mctash_stderr="${LOG_DIR}/mctash/${name}.err"
  ash_status=0
  mctash_status=0

  if [[ ${ASH_ONLY} -eq 0 ]]; then
    ash_status=0
    if ! "${ASH_CMD[@]}" "${CASES_DIR}/${case}" >"${ash_stdout}" 2>"${ash_stderr}"; then
      ash_status=$?
    fi
  fi

  if [[ ${MCTASH_ONLY} -eq 0 ]]; then
    set +e
    eval "${MCTASH_CMD} \"${CASES_DIR}/${case}\"" >"${mctash_stdout}" 2>"${mctash_stderr}"
    mctash_status=$?
    set -e
  fi

  if [[ ${GENERATE_EXPECTED} -eq 1 ]]; then
    if [[ ${ASH_ONLY} -eq 1 ]]; then
      cp "${ash_stdout}" "${LOG_DIR}/expected/${name}.out"
      cp "${ash_stderr}" "${LOG_DIR}/expected/${name}.err"
      echo "Generated expected outputs for ${name}" >&2
    fi
    continue
  fi

  if [[ ${MCTASH_ONLY} -eq 0 && ${ASH_ONLY} -eq 0 ]]; then
    if [[ ${ash_status} -ne ${mctash_status} ]]; then
      echo "${name}: exit status mismatch ash=${ash_status} mctash=${mctash_status}" >&2
      RESULT=1
    fi
    if ! diff -u "${ash_stdout}" "${mctash_stdout}" >"${LOG_DIR}/diff/${name}.out"; then
      echo "${name}: stdout mismatch" >&2
      RESULT=1
    fi
    if ! diff -u "${ash_stderr}" "${mctash_stderr}" >"${LOG_DIR}/diff/${name}.err"; then
      echo "${name}: stderr mismatch" >&2
      RESULT=1
    fi
  fi

done

exit "${RESULT}"
