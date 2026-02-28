#!/usr/bin/env ash
# Coverage: man ash 'alias', 'command', 'builtin', and 'unalias' (alias creation/removal, builtin escape, function fallback).
set -eu
norm_type() {
  type "$1" 2>/dev/null | sed 's/ is a shell function$/ is a function/'
}
oldcmd() { printf 'function-cmd\n'; }
alias oldcmd='printf "alias-cmd\\n"'
oldcmd
command printf 'command-printf\n'
norm_type oldcmd
unalias oldcmd
oldcmd
norm_type oldcmd
