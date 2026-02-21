#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHONPATH="${ROOT}/src" python3 -m mctash <<'EOF'
echo "smoke: hello"
x=world
echo "smoke: $x"
if echo ok; then echo "smoke: then"; fi
EOF
