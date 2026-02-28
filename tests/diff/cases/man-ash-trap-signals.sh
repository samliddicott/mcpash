#!/usr/bin/env ash
# Coverage: trap signal-name matrix.
# Areas:
# - install handlers for common signal names
# - clear handlers
# - verify trap listing retains EXIT handler
set -eu

trap 'echo trap-exit' EXIT
for sig in HUP INT QUIT TERM USR1 USR2; do
  trap ':' "$sig"
done

listing="$(trap)"
case "$listing" in
  *EXIT*trap-exit*) echo exit-set ;;
  *) echo exit-missing ;;
esac

for sig in HUP INT QUIT TERM USR1 USR2; do
  trap - "$sig"
done

listing2="$(trap)"
case "$listing2" in
  *EXIT*trap-exit*) echo exit-still-set ;;
  *) echo exit-cleared-bad ;;
esac
