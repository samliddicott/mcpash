#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage (bash --posix): caller/let/shopt command surface.

set +e

f() {
  caller
  caller 1
  caller 2 >/dev/null 2>&1
  echo "caller2:$?"
}
g() { f; }
g

let 'x=1+2'
echo "let1:$x:$?"
let '0'
echo "let0:$?"
let 'x+=4' 'x>0'
echo "letm:$x:$?"

shopt -s extglob
shopt -q extglob
echo "shq1:$?"
shopt -u extglob
shopt -q extglob
echo "shq2:$?"
shopt -p extglob
