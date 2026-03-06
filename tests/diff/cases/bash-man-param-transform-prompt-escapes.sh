#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage:
# - ${v@P} prompt escape universe for deterministic escapes.
# - Includes control escapes, prompt metadata escapes, and octal/\D{} forms.

set +e

x='\u|\h|\H|\w|\W|\$|\s|\!|\#|\j|\l|\101|\D{%Y}'
printf '<%s>\n' "${x@P}" | cat -vet

y='\a|\e|\n|\r|\\|\[x\]'
printf '<%s>\n' "${y@P}" | cat -vet
