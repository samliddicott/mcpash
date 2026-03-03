#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - positional parameter operators across set-empty/set-nonempty/unset
# - length and default/alternate forms
# - assignment/error operators on positional params (status-focused)
set -- "" one
echo "p1-:${1-x}|p1:-:${1:-x}|p1+:${1+y}|p1:+:${1:+y}|p1len:${#1}"
echo "p2-:${2-x}|p2:-:${2:-x}|p2+:${2+y}|p2:+:${2:+y}|p2len:${#2}"
echo "p9-:${9-x}|p9:-:${9:-x}|p9+:${9+y}|p9:+:${9:+y}|p9len:${#9}"

(echo "p1eq:${1=foo}") 2>/dev/null
echo "p1eq-status:$?"
(echo "p1ceq:${1:=foo}") 2>/dev/null
echo "p1ceq-status:$?"
(echo "p9err:${9?need9}") 2>/dev/null
echo "p9err-status:$?"
(echo "p9cerr:${9:?need9}") 2>/dev/null
echo "p9cerr-status:$?"
