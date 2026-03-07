#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.43.001: word expansion error fatality.
set +e
: "${NO_SUCH_VAR_43?boom43}" 2>/tmp/bcompat43.err
rc=$?
err="$(cat /tmp/bcompat43.err 2>/dev/null || true)"
rm -f /tmp/bcompat43.err
set -e
printf 'JM:BCOMPAT_43_001:rc=%s err=%s\n' "$rc" "$err"
echo 'JM:BCOMPAT_43_001:after'
