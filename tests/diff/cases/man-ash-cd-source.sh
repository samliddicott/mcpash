#!/usr/bin/env ash
# Coverage: man ash 'cd' and '.'/'source' builtins (relative/absolute directory changes, sourcing scripts).
set -euo pipefail
root=$(pwd)
mkdir -p tmpdir/subdir
cd tmpdir
printf 'inside=%s\n' "$(pwd)"
cd ../tmpdir/subdir
printf 'nested=%s\n' "$(pwd)"
cd "$root"
cat <<'SCRIPT' > tmpdir/source-me.sh
printf 'sourced=%s\n' "$SHELL"
SCRIPT
. "tmpdir/source-me.sh"
rm -rf tmpdir
