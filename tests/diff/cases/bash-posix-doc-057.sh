#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 57: kill -l one-line names without SIG prefix
out57="$(kill -l 2>/dev/null || true)"
if printf '%s' "$out57" | grep -q SIG; then echo JM:057:hasSIG; else echo JM:057:noSIG; fi
if printf '%s' "$out57" | grep -q $'
'; then echo JM:057:multiline; else echo JM:057:oneline; fi

