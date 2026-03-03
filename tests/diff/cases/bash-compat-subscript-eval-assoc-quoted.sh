#!/usr/bin/env bash
# DIFF_BASELINE: bash

# Coverage:
# - associative array keys with spaces/glob-like chars stay string keys
# - quoted and unquoted subscript forms resolve to same string key
declare -A map
map["a b"]=space
map['x*y']=glob
k='a b'
g='x*y'
echo "space:${map["a b"]}:${map[$k]}"
echo "glob:${map['x*y']}:${map[$g]}"
unset 'map[a b]'
echo "after-space:${map["a b"]-unset}:${map[$k]-unset}"
