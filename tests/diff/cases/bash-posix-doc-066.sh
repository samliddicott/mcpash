#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Item 66: `test -t` argument handling.
set +e
err_noarg="$(test -t 2>&1)"
rc_noarg=$?
test -t 1
rc_fd1=$?
set -e
printf 'JM:066:noarg-rc=%s noarg-err=%s\n' "$rc_noarg" "$err_noarg"
printf 'JM:066:fd1-rc=%s\n' "$rc_fd1"
