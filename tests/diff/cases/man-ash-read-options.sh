#!/usr/bin/env ash
# Coverage: read option support matrix for the active ash variant.
# Areas:
# - supported options: -r, -p
# - avoid variant-specific option coverage (-n, -d, -t differ across ash variants)
set -eu

set +e
read -r val <<'DATA1'
abc\\def
DATA1
st_r=$?

read -p prompt val <<'DATA2'
hello
DATA2
st_p=$?

set -e

printf 'read-r=%s\n' "$st_r"
printf 'read-p=%s\n' "$st_p"
