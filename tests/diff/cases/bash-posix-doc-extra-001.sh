#!/usr/bin/env bash
# DIFF_BASELINE: bash
set -euo pipefail

# Bash POSIX 6.11.2 extra row probe
# Requirement: BPOSIX.EXTRA.001
# Feature: POSIX requires that word splitting be byte-oriented.  That is, each _byte_ in the value of ‘IFS’ potentially splits a word, even if that byte is part of a multibyte character in ‘IFS’ or part of multibyte character in the word.  Bash allows multibyte characters in the value of ‘IFS’, treating a valid multibyte character as a single delimiter, and will not split a valid multibyte character even if one of the bytes composing that character appears in ‘IFS’. This is POSIX interpretation 1560, further modified by issue 1924.

echo 'JM:BPOSIX_EXTRA_001:probe'
