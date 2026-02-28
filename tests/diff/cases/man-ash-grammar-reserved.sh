#!/usr/bin/env ash
# Coverage: reserved-word contextualization and ambiguity.
# Areas:
# - reserved words used as literals in non-keyword positions
# - reserved-like tokens in loop/case contexts
# - reserved word rejection in function-name position
set -eu

# Literal positions.
echo then do in fi

# 'in' as loop variable name.
for in in a b; do
  echo loop:$in
done

# 'in' as case word and pattern token.
case in in
  in) echo case:ok ;;
esac

set +e
( eval 'function then { echo x; }' >/dev/null 2>&1 )
echo bad-fn-name=$?
( eval 'then() { echo x; }' >/dev/null 2>&1 )
echo bad-ksh-fn-name=$?
set -e
