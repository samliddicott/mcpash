#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): JOB CONTROL CHLD trap delivery across multiple children.

set +e

trap 'echo JM:chld' CHLD
sleep 0.05 & p1=$!
sleep 0.15 & p2=$!
wait "$p1"; echo JM:w1:$?
wait "$p2"; echo JM:w2:$?
echo JM:done
