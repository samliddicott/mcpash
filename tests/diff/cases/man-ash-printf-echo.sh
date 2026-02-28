#!/usr/bin/env ash
# Coverage: man ash 'print' (printf) and stable echo behaviors (-n, spacing).
set -eu
printf 'printf-line=%s\n' 'line1'
printf 'printf-multi=%s %s\n' 'two' 'parts'
printf 'printf-null=%s\n' ''
echo -n 'echo-inline'
echo ' echo-newline'
