#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TESTS_DIR="${ROOT}/tests"
OIL_DIR="${TESTS_DIR}/oil"
OIL_URL="https://github.com/oilshell/oil/archive/refs/heads/master.tar.gz"
OIL_TGZ="${OIL_DIR}/oils-master.tar.gz"
OIL_SRC="${OIL_DIR}/oils-master"
SPEC_DIR="${OIL_SRC}/spec"
SPEC_BIN="${SPEC_DIR}/bin"

fetch_if_missing() {
  if [[ -d "${SPEC_DIR}" ]]; then
    echo "Oil spec corpus already present in ${OIL_DIR}"
    return
  fi

  mkdir -p "${OIL_DIR}"
  if [[ ! -f "${OIL_TGZ}" ]]; then
    echo "Downloading Oil spec corpus..."
    wget -q -O "${OIL_TGZ}" "${OIL_URL}"
  fi

  rm -rf "${OIL_SRC}"
  echo "Unpacking Oil spec corpus..."
  tar -xzf "${OIL_TGZ}" -C "${OIL_DIR}"
}

run_subset() {
  local max_cases="${MAX_CASES:-0}"
  local specs=("$@")
  if [[ ${#specs[@]} -eq 0 ]]; then
    specs=(smoke redirect word-split)
  fi
  if [[ ! -e "${OIL_SRC}/tests" && -d "${OIL_SRC}/spec/testdata" ]]; then
    ln -s spec/testdata "${OIL_SRC}/tests"
  fi
  mkdir -p "${OIL_SRC}/_tmp"

  PYTHONPATH="${ROOT}/src" \
    python3 "${ROOT}/src/tests/oil_subset_runner.py" \
      --spec-root "${SPEC_DIR}" \
      --workdir "${OIL_SRC}" \
      --shell-cmd "python3 -m mctash" \
      --max-cases "${max_cases}" \
      --helper-path "${SPEC_BIN}" \
      "${specs[@]}"
}

mode="${1:-run}"
shift || true

case "${mode}" in
  fetch)
    fetch_if_missing
    ;;
  run)
    fetch_if_missing
    run_subset "$@"
    ;;
  *)
    echo "Usage: $0 [fetch|run] [spec-name ...]" >&2
    exit 2
    ;;
esac
