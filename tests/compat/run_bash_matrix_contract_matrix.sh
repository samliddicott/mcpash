#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECK="${ROOT}/scripts/check_bash_matrix_contract.py"

rows=(
  C12.MATRIX.01
  C12.MATRIX.02
  C12.MATRIX.03
  C12.MATRIX.04
  C12.MATRIX.05
  C12.MATRIX.06
  C12.MATRIX.07
)

for r in "${rows[@]}"; do
  python3 "$CHECK" --req "$r"
done

echo "[PASS] bash matrix contract matrix"
