#!/usr/bin/env ash
# Coverage: man ash 'eval' and 'exec' builtins (command evaluation, replacing shell process).
set -euo pipefail
VAR=echo
eval 'printf "eval-run=%s\n" "${VAR}"'
printf 'before-exec\n'
exec printf 'exec-run=done\n'
