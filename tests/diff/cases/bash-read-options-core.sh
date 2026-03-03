#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: bash-mode read option surface and semantics.
set +e

printf 'a b c\n' | {
  read -a arr
  st=$?
  printf 'a=%s,%s,%s,%s\n' "$st" "${#arr[@]}" "${arr[0]-}" "${arr[2]-}"
}

printf 'ab:cd\n' | {
  read -d : d
  st=$?
  printf 'd=%s,%s\n' "$st" "$d"
}

printf 'abcdef\n' | {
  read -n 3 n
  st=$?
  printf 'n=%s,%s\n' "$st" "$n"
}

printf 'abcdef\n' | {
  read -N 3 N
  st=$?
  printf 'N=%s,%s\n' "$st" "$N"
}

printf 'ab' | {
  read -n 3 np
  st=$?
  printf 'np=%s,%s\n' "$st" "$np"
}

printf 'ab' | {
  read -N 3 Np
  st=$?
  printf 'Np=%s,%s\n' "$st" "$Np"
}

tmp="$(mktemp)"
printf 'qq rr\n' >"$tmp"
exec 3<"$tmp"
read -u 3 u1 u2
st=$?
exec 3<&-
rm -f "$tmp"
printf 'u=%s,%s,%s\n' "$st" "$u1" "$u2"

printf 'abc\n' | {
  read -s s
  st=$?
  printf 's=%s,%s\n' "$st" "$s"
}

printf 'abc\n' | {
  read -e -i zzz e
  st=$?
  printf 'e=%s,%s\n' "$st" "$e"
}

p2="$(mktemp -u)"
mkfifo "$p2"
{ exec 8>"$p2"; sleep 1; } &
read -t 0.05 t <"$p2"
st=$?
rm -f "$p2"
printf 't=%s,%s\n' "$st" "${t-}"
