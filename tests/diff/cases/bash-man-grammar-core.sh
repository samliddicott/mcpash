#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: grammar core productions (simple/pipeline/lists/if/while/until/for/case/functions/subshell/group)

set +e

echo simple
echo A | cat
false && echo and-bad || echo and-or-ok
( echo subshell )
{ echo group; }

x=2
if [ "$x" -eq 2 ]; then
  echo if-then
elif [ "$x" -eq 3 ]; then
  echo if-elif
else
  echo if-else
fi

i=0
while [ "$i" -lt 1 ]; do
  echo while:$i
  i=$((i+1))
done

j=0
until [ "$j" -ge 1 ]; do
  echo until:$j
  j=$((j+1))
done

for a in one two; do
  echo for-in:$a
done

set -- p q
for a; do
  echo for-pos:$a
done

case foo in
  f*) echo case:match ;;
  *) echo case:other ;;
esac

f_core() { echo func:$1; }
f_core z
