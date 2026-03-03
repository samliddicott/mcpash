#!/usr/bin/env ash
# Coverage: trap handler delivery for named and numeric signals.
# Areas:
# - install/execute trap for signal name and number
# - clear trap entries after use
set -eu

trap 'echo us1' USR1
kill -USR1 $$

trap 'echo us2' 10
kill -10 $$

trap - USR1 10
echo done
