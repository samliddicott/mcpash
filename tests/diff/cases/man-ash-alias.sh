#!/usr/bin/env ash
# Coverage: man ash 'alias', 'command', and 'builtin' (alias creation, overriding, builtin escape).
set -euo pipefail
oldcmd() { printf 'function-cmd\n'; }
alias oldcmd='printf alias-cmd\n'
oldcmd
command oldcmd
builtin printf 'builtin-printf\n'
alias | grep oldcmd
