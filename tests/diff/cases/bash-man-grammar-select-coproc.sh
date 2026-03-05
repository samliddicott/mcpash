#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: bash grammar extensions select and coproc

set +e

PS3='pick> '
printf '1\n' | {
  select item in alpha beta; do
    echo "select:${item:-none}"
    break
  done
}

coproc CP { echo coproc-hello; }
read -r line <&"${CP[0]}"
echo "coproc:${line:-}"
wait "$CP_PID" 2>/dev/null || true
