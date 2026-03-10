#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.43.001: word expansion error fatality.
set +e
{ : "${NO_SUCH_VAR_43?boom43}"; } 2>/tmp/bcompat43.err
rc=$?
err="$(cat /tmp/bcompat43.err 2>/dev/null || true)"
rm -f /tmp/bcompat43.err
set -e
case "$err" in
  *boom43*) has_boom=1 ;;
  *) has_boom=0 ;;
esac
printf 'JM:BCOMPAT_43_001:rc=%s boom=%s\n' "$rc" "$has_boom"
