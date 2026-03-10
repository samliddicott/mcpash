#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# BCOMPAT.50.001: RANDOM sequence when seeded.
RANDOM=17
a=$RANDOM
b=$RANDOM
c=$RANDOM
d=$RANDOM
if [ "$a" != "$b" ]; then advances=1; else advances=0; fi
ok_range=1
for n in "$a" "$b" "$c" "$d"; do
  if [ "$n" -lt 0 ] || [ "$n" -gt 32767 ]; then
    ok_range=0
  fi
done
echo "JM:BCOMPAT_50_001:advances=$advances range=$ok_range"
