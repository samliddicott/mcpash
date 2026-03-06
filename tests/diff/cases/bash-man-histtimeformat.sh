#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - HISTTIMEFORMAT affects history output timestamp prefix.
# - history -s entries retain timestamp formatting.

set +e
history -c
HISTTIMEFORMAT='%Y-%m-%d '
history -s alpha
history -s beta
history | sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/DATE/g'
