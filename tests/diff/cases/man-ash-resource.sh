#!/usr/bin/env ash
# Coverage: man ash hash, times, ulimit, umask builtins.
# Areas:
# - hash cache reset/query and not-found status
# - times command status
# - umask get/set/get roundtrip
# - ulimit query and no-op set path
set -eu
hash -r
hash ls >/dev/null
printf 'hash-status=%s\n' "$?"
set +e
hash definitely_not_a_cmd >/dev/null 2>&1
hash_missing=$?
set -e
printf 'hash-missing=%s\n' "$hash_missing"

times >/dev/null
printf 'times-status=%s\n' "$?"

orig_umask="$(umask)"
umask 022
printf 'umask-now=%s\n' "$(umask)"
umask "$orig_umask"
printf 'umask-restore=%s\n' "$(umask)"

nofile="$(ulimit -n)"
printf 'ulimit-n=%s\n' "$nofile"
if [ "$nofile" != "unlimited" ]; then
  ulimit -n "$nofile"
  printf 'ulimit-set=same\n'
else
  printf 'ulimit-set=skip\n'
fi
