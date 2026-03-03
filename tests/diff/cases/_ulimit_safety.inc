#!/usr/bin/env ash
# Safety helper for ulimit differential tests.
# Applies conservative soft-limit caps for the shell process under test.

cap_soft_limit() {
  flag="$1"
  cap="$2"
  cur="$(ulimit -S -"$flag" 2>/dev/null || echo "")"
  case "$cur" in
    "" ) return 0 ;;
    unlimited) ulimit -S -"$flag" "$cap" >/dev/null 2>&1 || true; return 0 ;;
  esac
  case "$cur" in
    *[!0-9]* ) return 0 ;;
  esac
  if [ "$cur" -gt "$cap" ]; then
    ulimit -S -"$flag" "$cap" >/dev/null 2>&1 || true
  fi
}

apply_ulimit_safety_caps() {
  # Keep resource ceilings conservative to avoid stress/hangs during tests.
  cap_soft_limit t 60        # CPU seconds
  cap_soft_limit f 1024      # file blocks (512-byte units)
  cap_soft_limit c 0         # core file blocks
  cap_soft_limit d 262144    # data kbytes
  cap_soft_limit s 8192      # stack kbytes
  cap_soft_limit l 65536     # locked memory kbytes
  cap_soft_limit m 262144    # memory kbytes
  cap_soft_limit p 1024      # processes
  cap_soft_limit n 1024      # open files
  cap_soft_limit v 524288    # vmemory kbytes
}
