#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: process substitution <(...) and >(...)

set +e

cat <(printf 'ps-in\n')
outf="${TMPDIR:-/tmp}/mctash-ps-$$"
cat >("cat > '$outf'") <<'EOD'
ps-out
EOD
cat "$outf"
rm -f "$outf"
