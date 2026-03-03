#!/usr/bin/env ash
# Coverage: ulimit -a listing surface for this comparator target.
# Areas:
# - broad resource listing includes expected rows
set -eu
. "$(dirname "$0")/_ulimit_safety.inc"
apply_ulimit_safety_caps

out="$(ulimit -a)"
case "$out" in
  *time\(seconds\)* ) echo row-time ;; * ) echo row-time-miss ;; esac
case "$out" in
  *file\(blocks\)* ) echo row-file ;; * ) echo row-file-miss ;; esac
case "$out" in
  *nofiles* ) echo row-nofile ;; * ) echo row-nofile-miss ;; esac
case "$out" in
  *vmemory\(kbytes\)* ) echo row-vmem ;; * ) echo row-vmem-miss ;; esac
