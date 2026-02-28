#!/usr/bin/env ash
# Coverage: simple command prefix/suffix interleaving.
# Areas:
# - assignment prefix on builtin
# - assignment prefix on function invocation
# - assignment prefix + redirection ordering
# - redirection before/after words in same simple command
set -eu

# Assignment prefix for builtin should not persist in shell.
X=1 export TMP_A=alpha
printf 'tmp-a=%s\n' "${TMP_A-}"
unset TMP_A

# Assignment prefix for function should be visible to function and persist for shell vars.
f_show() { printf 'f-x=%s\n' "${X-}"; }
X=local f_show
printf 'x-after-f=%s\n' "${X-}"

# Redirection with builtin in mixed position.
: > /tmp/mctash-prefix-$$.tmp
printf hi > /tmp/mctash-prefix-$$.tmp
printf 'file=%s\n' "$(cat /tmp/mctash-prefix-$$.tmp)"
rm -f /tmp/mctash-prefix-$$.tmp

# Prefix assignment with external command should not overwrite shell var.
Y=outer
Y=inner env | grep '^Y=' | sed 's/^/env-/'
printf 'y-after-ext=%s\n' "$Y"

# Interleaved redirects around command words.
printf one >/tmp/mctash-prefix-$$.a 2>/tmp/mctash-prefix-$$.b
printf 'a=%s\n' "$(cat /tmp/mctash-prefix-$$.a)"
printf 'b=%s\n' "$(wc -c < /tmp/mctash-prefix-$$.b | tr -d ' ')"
rm -f /tmp/mctash-prefix-$$.a /tmp/mctash-prefix-$$.b
