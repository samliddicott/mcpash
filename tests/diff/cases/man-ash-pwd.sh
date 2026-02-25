#!/usr/bin/env ash
# Coverage: man ash `pwd` builtin (absolute and relative path reports, PWD variable accuracy).
set -euo pipefail
root=$(pwd)
cd /
pwd
cd "$root"
pwd
printf 'pwd-var=%s\n' "$PWD"
