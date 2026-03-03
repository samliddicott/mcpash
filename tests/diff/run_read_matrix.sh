#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="${ROOT}/tests/diff/run.sh"

# Ash-family comparators for ash-target read semantics.
ash_comparators=(ash)
for c in dash; do
  if command -v "$c" >/dev/null 2>&1; then
    ash_comparators+=("$c")
  fi
done
if command -v busybox >/dev/null 2>&1; then
  ash_comparators+=("busybox ash")
fi

echo "[read-matrix] ash-family comparators: ${ash_comparators[*]}"
for comp in "${ash_comparators[@]}"; do
  echo "[read-matrix] ash-lane comparator: $comp"
  ASH_BIN="$comp" "$RUNNER" \
    --case man-ash-read.sh \
    --case man-ash-read-options.sh \
    --case man-ash-read-ifs-matrix.sh
  if [[ "$comp" == "ash" || "$comp" == "dash" ]]; then
    ASH_BIN="$comp" "$RUNNER" --case man-ash-read-option-probe.sh
  else
    echo "[read-matrix] skip option-probe parity for comparator: $comp (option surface differs by implementation)"
  fi
done

echo "[read-matrix] bash comparator lane"
PARITY_BASH_COMPAT=50 PARITY_MIRROR_POSIX=1 BASH_BIN="bash --posix" "$RUNNER" \
  --case bash-read-options-core.sh

echo "[read-matrix] ok"
