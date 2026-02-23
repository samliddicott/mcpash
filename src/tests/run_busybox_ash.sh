#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TESTS_DIR="${ROOT}/tests"
BUSYBOX_DIR="${TESTS_DIR}/busybox"
BUSYBOX_URL="https://github.com/mirror/busybox/archive/refs/heads/master.tar.gz"
BUSYBOX_TGZ="${BUSYBOX_DIR}/busybox-master.tar.gz"
BUSYBOX_SRC="${BUSYBOX_DIR}/busybox-master"
ASH_TEST_DIR="${BUSYBOX_DIR}/ash_test"
HUSH_TEST_DIR="${BUSYBOX_DIR}/hush_test"
ASH_LOG="${ASH_TEST_DIR}/mctash-ash.log"
RUN_TIMEOUT="${RUN_TIMEOUT:-120}"

fetch_if_missing() {
  if [[ -d "${ASH_TEST_DIR}" && -d "${HUSH_TEST_DIR}" ]]; then
    echo "BusyBox tests already present in ${BUSYBOX_DIR}"
    return
  fi

  mkdir -p "${BUSYBOX_DIR}"
  if [[ ! -f "${BUSYBOX_TGZ}" ]]; then
    echo "Downloading BusyBox test corpus..."
    wget -q -O "${BUSYBOX_TGZ}" "${BUSYBOX_URL}"
  fi

  rm -rf "${BUSYBOX_SRC}"
  echo "Unpacking BusyBox test corpus..."
  tar -xzf "${BUSYBOX_TGZ}" -C "${BUSYBOX_DIR}"
  rm -rf "${ASH_TEST_DIR}" "${HUSH_TEST_DIR}"
  cp -a "${BUSYBOX_SRC}/shell/ash_test" "${ASH_TEST_DIR}"
  cp -a "${BUSYBOX_SRC}/shell/hush_test" "${HUSH_TEST_DIR}"
  echo "Installed BusyBox tests to ${BUSYBOX_DIR}"
}

run_ash() {
  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'set -euo pipefail' \
    "PYTHONPATH=\"${ROOT}/src\" exec python3 -m mctash \"\$@\"" \
    > "${ASH_TEST_DIR}/ash"
  chmod +x "${ASH_TEST_DIR}/ash"
  cat > "${ASH_TEST_DIR}/.config" <<'EOF'
CONFIG_FEATURE_FANCY_ECHO=y
EOF

  cd "${ASH_TEST_DIR}"
  set +e
  set -o pipefail
  timeout "${RUN_TIMEOUT}" ./run-all 2>&1 | tee "${ASH_LOG}"
  rc=${PIPESTATUS[0]}
  set -e

  ok=$(grep -c ' ok$' "${ASH_LOG}" || true)
  fail=$(grep -c ' fail' "${ASH_LOG}" || true)
  skip=$(grep -c ' skip ' "${ASH_LOG}" || true)
  echo "Summary: ok=${ok} fail=${fail} skip=${skip}"
  if [[ ${rc} -eq 124 ]]; then
    echo "Timed out after ${RUN_TIMEOUT}s"
  fi
  return "${rc}"
}

mode="${1:-run}"
case "${mode}" in
  fetch)
    fetch_if_missing
    ;;
  run)
    fetch_if_missing
    run_ash
    ;;
  *)
    echo "Usage: $0 [fetch|run]" >&2
    exit 2
    ;;
esac
