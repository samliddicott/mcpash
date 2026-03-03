#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT="${ROOT}/docs/reports/trap-variant-matrix-latest.md"

comparators=("ash" "dash" "bash --posix" "busybox ash")
signals=(HUP INT QUIT TERM USR1 USR2 ALRM PIPE)

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT

have_cmp=()
for c in "${comparators[@]}"; do
  base="${c%% *}"
  if command -v "$base" >/dev/null 2>&1; then
    have_cmp+=("$c")
  fi
done

run_one() {
  local cmd="$1"
  local src="$2"
  local out="$3"
  local -a cmd_arr=()
  read -r -a cmd_arr <<<"$cmd"
  set +e
  "${cmd_arr[@]}" -c "$src" >"$out" 2>&1
  local rc=$?
  set -e
  echo "$rc"
}

{
  echo "# Trap Variant Matrix Report"
  echo
  echo "Generated: $(date -u +"%Y-%m-%d %H:%M:%SZ")"
  echo
  echo "Comparators: ${have_cmp[*]}"
  echo
  echo "| Comparator | Signal | RC | Marker |"
  echo "|---|---:|---:|---|"
  for c in "${have_cmp[@]}"; do
    for s in "${signals[@]}"; do
      out="$tmpdir/$(echo "$c" | tr ' /' '__').${s}.out"
      src="trap 'echo VM:GOT:$s' $s; kill -$s \$\$; echo VM:END"
      rc="$(run_one "$c" "$src" "$out")"
      marker="$(grep '^VM:' "$out" | tr '\n' ';' || true)"
      marker="${marker//|/\\|}"
      echo "| \`$c\` | \`$s\` | $rc | \`${marker}\` |"
    done
  done
} >"$REPORT"

echo "[INFO] wrote $REPORT"
echo "[PASS] trap variant matrix"
