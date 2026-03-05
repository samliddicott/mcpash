#!/usr/bin/env ash
# DIFF_BASELINE: bash
# Coverage: dirs/pushd/popd core stack semantics.
set +e

base="${TMPDIR:-/tmp}/mctash-ds-$$"
mkdir -p "$base/d1" "$base/d2" "$base/d3"

cd "$base/d1" || exit 1
pushd "$base/d2" >/dev/null
pushd "$base/d3" >/dev/null

s1=$(dirs -p | awk -F/ '{print $NF}' | paste -sd, -)

pushd >/dev/null
s2=$(dirs -p | awk -F/ '{print $NF}' | paste -sd, -)

popd >/dev/null
s3=$(dirs -p | awk -F/ '{print $NF}' | paste -sd, -)

dplus=$(basename "$(dirs +1)")
dminus=$(basename "$(dirs -0)")

popd +1 >/dev/null
s4=$(dirs -p | awk -F/ '{print $NF}' | paste -sd, -)
pwd_base=$(basename "$PWD")

printf 'ds:%s|%s|%s|%s|%s|%s|%s\n' "$s1" "$s2" "$s3" "$dplus" "$dminus" "$s4" "$pwd_base"

rm -rf "$base"
