#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: brace expansion and locale translation quoting ($"...")

set +e

echo brace:a{b,c}d
printf 'locale:%s\n' "$\"hello\""
