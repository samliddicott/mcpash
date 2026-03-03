#!/usr/bin/env ash
# Coverage: read option probe matrix for this comparator target.
# Areas:
# - probe support/status for -n, -d, -t without assuming universal availability
set -e

set +e
read -n 1 _n 2>/dev/null <<'DATA'
xyz
DATA
st_n=$?

read -d : _d 2>/dev/null <<'DATA2'
ab:cd
DATA2
st_d=$?

read -t 0 _t 2>/dev/null <<'DATA3'
qq
DATA3
st_t=$?
set -e

printf 'read-opt-n=%s\n' "$st_n"
printf 'read-opt-d=%s\n' "$st_d"
printf 'read-opt-t=%s\n' "$st_t"
