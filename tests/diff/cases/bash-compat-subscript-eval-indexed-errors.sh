#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - invalid indexed arithmetic (divide by zero, invalid base digits)
# - non-success status in expression contexts while script continues
declare -a arr
arr[0]=x

(echo "div0:${arr[1/0]-unset}") 2>/dev/null
echo "div0-status:$?"

(echo "badbase:${arr[08]-unset}") 2>/dev/null
echo "badbase-status:$?"
