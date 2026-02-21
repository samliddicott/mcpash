#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROOT
TEST_DIR="${ROOT}/external/ash-shell-test"

if [[ ! -d "${TEST_DIR}" ]]; then
  echo "ash-shell-test submodule not found. Run:"
  echo "  git submodule update --init --recursive"
  exit 1
fi

PYTHONPATH="${ROOT}/src" exec python3 -m mctash "${ROOT}/scripts/ash-test-runner.sh"
