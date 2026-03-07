#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 65: `test` string comparison is locale-sensitive.
set +e
LC_ALL=C test Z '<' a
rc_c=$?
LC_ALL=C test a '>' Z
rc_c_rev=$?
# Use first available non-C locale to probe behavior if present.
loc="$(locale -a 2>/dev/null | grep -E '^(en_US|C\.UTF-8|POSIX|C)(\.UTF-8)?$' | head -n1 || true)"
if [ -n "$loc" ]; then
  LC_ALL="$loc" test Z '<' a
  rc_l=$?
else
  rc_l=255
fi
set -e
printf 'JM:065:C:%s CREV:%s L:%s(%s)\n' "$rc_c" "$rc_c_rev" "$rc_l" "${loc:-none}"
