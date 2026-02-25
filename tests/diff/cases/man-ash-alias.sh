#!/usr/bin/env ash
# Coverage: man ash 'alias', 'command', 'builtin', and 'unalias' (alias creation/removal, builtin escape, function fallback).
set -euo pipefail
oldcmd() { printf 'function-cmd\n'; }
alias oldcmd='printf alias-cmd\n'
oldcmd
command oldcmd
builtin printf 'builtin-printf\n'
alias | grep oldcmd >/dev/null
printf 'alias-ok\n'
unalias oldcmd
oldcmd
type oldcmd
