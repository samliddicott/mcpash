#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: set -o option surface (query/set/unset) and short-option aliases

set +e

for o in allexport braceexpand emacs errexit errtrace functrace hashall histexpand history ignoreeof interactive-comments keyword monitor noclobber noglob nolog notify nounset onecmd physical pipefail posix privileged verbose vi xtrace; do
  (
    if [ "$o" = xtrace ]; then
      exec 2>/dev/null
    fi
    set -o "$o" 2>/dev/null
    rc_on=$?
    set +o "$o" 2>/dev/null
    rc_off=$?
    set -o 2>/dev/null | awk -v k="$o" '$1==k {print "seto:"k":"$2}'
    echo "seto-rc:$o:$rc_on:$rc_off"
  )
done

for s in a e f n u v x B C E H P T; do
  (
    if [ "$s" = x ]; then
      exec 2>/dev/null
    fi
    set "-$s"
    rc_on=$?
    set "+$s"
    rc_off=$?
    echo "short:$s:$rc_on:$rc_off"
  )
done
