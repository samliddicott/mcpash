#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: process substitution <(...) and >(...)

set +e

cat <(printf 'ps-in\n')
printf 'ps-out\n' > >(cat >/dev/null)
