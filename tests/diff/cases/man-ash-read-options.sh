#!/usr/bin/env ash
# Coverage: read option support matrix for the active ash variant.
# Areas:
# - supported options: -r, -p
# - unsupported options: -n, -d, -t (status parity)
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

read -n 1 val 2>/dev/null <<'DATA3'
x
DATA3
st_n=$?

read -d , val 2>/dev/null <<'DATA4'
a,b
DATA4
st_d=$?

read -t 0 val 2>/dev/null <<'DATA5'
z
DATA5
st_t=$?
set -e

printf 'read-r=%s\n' "$st_r"
printf 'read-p=%s\n' "$st_p"
printf 'read-n=%s\n' "$st_n"
printf 'read-d=%s\n' "$st_d"
printf 'read-t=%s\n' "$st_t"
