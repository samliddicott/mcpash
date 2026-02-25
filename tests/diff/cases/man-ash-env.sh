#!/usr/bin/env ash
# Coverage: man ash export, unset, readonly builtins (exporting, unexporting, readonly protection).
set -eu
VAR_EXPORT=done
export VAR_EXPORT
printf 'exported=%s\n' "$VAR_EXPORT"

if unset VAR_EXPORT 2>/dev/null; then
  printf 'unset-exported=ok\n'
else
  printf 'unset-exported=fail\n'
fi

readonly FIXED=constant
if (unset FIXED >/dev/null 2>&1); then
  printf 'unset-readonly=ok\n'
else
  printf 'unset-readonly=blocked\n'
fi
printf 'readonly-val=%s\n' "$FIXED"

export TEMP_VAR=tmp
unset TEMP_VAR
if [ -z "${TEMP_VAR+set}" ]; then
  printf 'exported-removed\n'
else
  printf 'exported-still=%s\n' "$TEMP_VAR"
fi
