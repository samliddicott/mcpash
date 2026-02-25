#!/usr/bin/env ash
# Coverage: man ash 'alias', 'command', 'builtin', and 'unalias' (alias creation/removal, builtin escape, function fallback).
set -eu
oldcmd() { printf 'function-cmd\n'; }
alias oldcmd='printf "alias-cmd\\n"'
oldcmd
command printf 'command-printf\n'
type oldcmd
unalias oldcmd
oldcmd
type oldcmd
