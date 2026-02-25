#!/usr/bin/env ash
# Coverage: man ash ':' (no-op), 'true', 'false', 'exit', 'break', 'continue', 'return' plus loop control.
: # no-op should succeed
if true && :; then printf 'true-passed\n'; fi
afternoon_try=false
if ! false; then printf 'false-negated\n'; fi
for i in 1 2 3; do
  if [ "$i" -eq 2 ]; then continue; fi
  printf 'loop=%s\n' "$i"
  if [ "$i" -eq 3 ]; then break; fi
done
func_ret() {
  return 3
}
if func_ret; then
  :
else
  printf 'return-status=%s\n' "$?"
fi
if (exit 7); then
  :
else
  printf 'sub-exit=%s\n' "$?"
fi
