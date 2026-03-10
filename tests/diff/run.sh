#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASES_DIR="${ROOT}/tests/diff/cases"
LOG_DIR="${ROOT}/tests/diff/logs"
ASH_BIN="${ASH_BIN:-ash}"
read -r -a ASH_CMD <<< "${ASH_BIN}"
BASH_BIN="${BASH_BIN:-bash --posix}"
read -r -a BASH_CMD <<< "${BASH_BIN}"
MCTASH_CMD="${MCTASH_CMD:-PYTHONPATH=${ROOT}/src python3 -m mctash}"
MCTASH_MODE_DEFAULT="${MCTASH_MODE_DEFAULT:-posix}"
MCTASH_BACKEND="${MCTASH_BACKEND:-interpreter}"
PARITY_BASH_COMPAT="${PARITY_BASH_COMPAT:-}"
PARITY_MIRROR_POSIX="${PARITY_MIRROR_POSIX:-0}"

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
  for filter in "${CASE_FILTER[@]}"; do
    exact_name="${filter%.sh}.sh"
    exact_hits=()
    for case in "${CASE_FILES[@]}"; do
      [[ "${case}" == "${exact_name}" ]] && exact_hits+=("${case}")
    done
    if [[ ${#exact_hits[@]} -gt 0 ]]; then
      FILTERED+=("${exact_hits[@]}")
      continue
    fi
    for case in "${CASE_FILES[@]}"; do
      [[ "${case}" == *"${filter}"* ]] && FILTERED+=("${case}")
    done
  done
  # Deduplicate while preserving order.
  if [[ ${#FILTERED[@]} -gt 0 ]]; then
    mapfile -t FILTERED < <(printf '%s\n' "${FILTERED[@]}" | awk '!seen[$0]++')
  fi
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
  compare_name="ash"
  compare_cmd=("${ASH_CMD[@]}")
  if grep -q '^# DIFF_BASELINE: bash$' "${CASES_DIR}/${case}"; then
    compare_name="bash"
    compare_cmd=("${BASH_CMD[@]}")
    if [[ "${PARITY_MIRROR_POSIX}" == "1" ]]; then
      has_posix=0
      for a in "${compare_cmd[@]}"; do
        [[ "$a" == "--posix" ]] && has_posix=1 && break
      done
      [[ "$has_posix" -eq 1 ]] || compare_cmd+=("--posix")
    fi
  fi

  if [[ ${ASH_ONLY} -eq 0 ]]; then
    set +e
    if [[ "${compare_name}" == "bash" && -n "${PARITY_BASH_COMPAT}" ]]; then
      env BASH_COMPAT="${PARITY_BASH_COMPAT}" "${compare_cmd[@]}" "${CASES_DIR}/${case}" >"${ash_stdout}" 2>"${ash_stderr}"
      ash_status=$?
    else
      "${compare_cmd[@]}" "${CASES_DIR}/${case}" >"${ash_stdout}" 2>"${ash_stderr}"
      ash_status=$?
    fi
    set -e
  fi

  if [[ ${MCTASH_ONLY} -eq 0 ]]; then
    mctash_prefix=""
    mctash_opts=""
    mctash_mode="${MCTASH_MODE_DEFAULT}"
    if [[ "${compare_name}" == "bash" && -n "${PARITY_BASH_COMPAT}" ]]; then
      mctash_mode="bash"
      mctash_prefix="BASH_COMPAT=${PARITY_BASH_COMPAT} "
    else
      # Keep ash/posix lane deterministic even if caller env exports BASH_COMPAT.
      mctash_prefix="BASH_COMPAT= "
    fi
    mctash_prefix="MCTASH_BACKEND=${MCTASH_BACKEND} MCTASH_MODE=${mctash_mode} ${mctash_prefix}"
    if [[ "${PARITY_MIRROR_POSIX}" == "1" ]]; then
      mctash_opts="--posix "
    fi
    set +e
    eval "${mctash_prefix}${MCTASH_CMD} ${mctash_opts}\"${CASES_DIR}/${case}\"" >"${mctash_stdout}" 2>"${mctash_stderr}"
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
      echo "${name}: exit status mismatch ${compare_name}=${ash_status} mctash=${mctash_status}" >&2
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
