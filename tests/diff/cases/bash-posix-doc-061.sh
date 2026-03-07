#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
# Item 61: pwd verifies printed value matches cwd
pwdout="$(pwd)"
if [[ -d "$pwdout" ]]; then echo JM:061:dir; else echo JM:061:nodir; fi

