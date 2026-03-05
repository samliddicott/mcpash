#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: set -o option surface (query/set/unset) and short-option aliases

set +e

opts='allexport braceexpand emacs errexit errtrace functrace hashall histexpand history ignoreeof interactive-comments keyword monitor noclobber noexec noglob nolog notify nounset onecmd physical pipefail posix privileged verbose vi xtrace'
for o in $opts; do
  set -o "$o" 2>/dev/null
  rc_on=$?
  set +o "$o" 2>/dev/null
  rc_off=$?
  set -o | awk -v k="$o" '$1==k {print "seto:"k":"$2}'
  echo "seto-rc:$o:$rc_on:$rc_off"
done

set -a; set +a; echo short:a
set -e; set +e; echo short:e
set -f; set +f; echo short:f
set -n; set +n; echo short:n
set -u; set +u; echo short:u
set -v; set +v; echo short:v
set -x; set +x; set +x; echo short:x
set -B; set +B; echo short:B
set -C; set +C; echo short:C
set -E; set +E; echo short:E
set -H; set +H; echo short:H
set -P; set +P; echo short:P
set -T; set +T; echo short:T
