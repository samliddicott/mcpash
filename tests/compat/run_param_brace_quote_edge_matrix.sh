#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORT="${ROOT}/docs/reports/param-brace-quote-edge-matrix-latest.md"

python3 - <<'PY'
from __future__ import annotations

import datetime as _dt
import subprocess
from pathlib import Path

ROOT = Path("/home/sam/Projects/pybash")
REPORT = ROOT / "docs/reports/param-brace-quote-edge-matrix-latest.md"

CASES: list[dict[str, str]] = [
    {
        "id": "E001",
        "desc": "simple default expansion baseline",
        "code": "unset v; printf '<%s>\\n' \"${v-default}\"",
    },
    {
        "id": "E002",
        "desc": "single quote chars in operator word",
        "code": "printf '<%s>\\n' \"${IFS+'}'z}\"",
    },
    {
        "id": "E003",
        "desc": "unmatched single quote inside operator word",
        "code": "printf '<%s>\\n' \"${IFS+'bar} baz\"",
    },
    {
        "id": "E004",
        "desc": "double-quoted operator word containing escaped quote",
        "code": "printf '<%s>\\n' \"${IFS+\\\"\\}\\\"z}\"",
    },
    {
        "id": "E005",
        "desc": "exact upstream mixed quote toggles with comment tail",
        "code": "(echo -n '28 '; printf '%s\\n' \"${IFS+\"'\"x ~ x'}'x\"'}\"x}\" #')",
    },
    {
        "id": "E006",
        "desc": "operator word with command substitution",
        "code": "l=t; printf '<%s>\\n' \"${IFS+h$(echo -n i ${IFS+$l}h)ere}\"",
    },
    {
        "id": "E007",
        "desc": "operator word with backticks and nested ${...}",
        "code": "l=t; printf '<%s>\\n' \"${IFS+h`echo -n i ${IFS+$l}h`ere}\"",
    },
    {
        "id": "E008",
        "desc": "operator word with nested brace expansion",
        "code": "printf '<%s>\\n' \"${IFS+foo ${IFS+bar} baz}\"",
    },
    {
        "id": "E009",
        "desc": "parameter replace with quote char in pattern",
        "code": "foo=\"x'a'y\"; printf '<%s>\\n' \"${foo%*'a'*}\"",
    },
    {
        "id": "E010",
        "desc": "single quotes in unquoted expansion word",
        "code": "key=value; printf '<%s>\\n' ${IFS+'$key'}",
    },
    {
        "id": "E011",
        "desc": "single quotes in quoted expansion word",
        "code": "key=value; printf '<%s>\\n' \"${IFS+'$key'}\"",
    },
    {
        "id": "E012",
        "desc": "line continuation inside ${...} word (single quotes)",
        "code": "printf '<%s>\\n' ${IFS+foo 'b\\\nar' baz}",
    },
    {
        "id": "E013",
        "desc": "line continuation inside ${...} word (double quotes)",
        "code": "printf '<%s>\\n' ${IFS+foo \"b\\\nar\" baz}",
    },
    {
        "id": "E014",
        "desc": "braced op with escaped right brace",
        "code": "printf '<%s>\\n' ${IFS+\\}z}",
    },
    {
        "id": "E015",
        "desc": "double-quoted braced op with escaped right brace",
        "code": "printf '<%s>\\n' \"${IFS+\\}z}\"",
    },
    {
        "id": "E016",
        "desc": "malformed: missing close brace",
        "code": "printf '%s\\n' \"${IFS+abc\"",
    },
    {
        "id": "E017",
        "desc": "malformed: bad parameter name",
        "code": "printf '%s\\n' \"${+x}\"",
    },
    {
        "id": "E018",
        "desc": "malformed: unterminated quote in braced op word",
        "code": "printf '%s\\n' \"${IFS+\\\"abc}\"",
    },
]


def _sh_escape(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"


def _one_line(s: str) -> str:
    s = s.replace("\\", "\\\\").replace("\n", "\\n")
    return s if len(s) <= 120 else s[:117] + "..."


def _err_class(s: str) -> str:
    t = s.lower()
    if "bad substitution" in t:
        return "bad_substitution"
    if "unterminated quoted string" in t or "unexpected eof while looking for matching" in t or "unexpected end of file" in t:
        return "unterminated_quote"
    if "syntax error" in t:
        return "syntax_error"
    return "none" if not t.strip() else "other"


def run_case(shell_kind: str, code: str) -> tuple[int, str, str]:
    if shell_kind == "bash":
        cmd = [
            "timeout",
            "-k",
            "2",
            "8",
            "bash",
            "--posix",
            "-c",
            f"set -o posix; shopt -u xpg_echo 2>/dev/null || true; {code}",
        ]
        env = None
    else:
        cmd = [
            "timeout",
            "-k",
            "2",
            "8",
            "env",
            "PYTHONPATH=/home/sam/Projects/pybash/src",
            "MCTASH_MODE=posix",
            "MCTASH_DIAG_STYLE=bash",
            "MCTASH_MAX_VMEM_KB=262144",
            "python3",
            "-m",
            "mctash",
            "--posix",
            "-c",
            code,
        ]
        env = None
    p = subprocess.run(cmd, text=True, capture_output=True, env=env)
    return p.returncode, p.stdout, p.stderr


rows: list[str] = []
full = 0
for case in CASES:
    b_rc, b_out, b_err = run_case("bash", case["code"])
    m_rc, m_out, m_err = run_case("mctash", case["code"])
    malformed = case["desc"].startswith("malformed:")
    if malformed:
        ok = b_rc == m_rc and b_out == m_out and _err_class(b_err) == _err_class(m_err)
    else:
        ok = b_rc == m_rc and b_out == m_out and b_err == m_err
    if ok:
        full += 1
    rows.append(
        "| `{id}` | {desc} | `{brc}` | `{mrc}` | `{bout}` | `{mout}` | `{berr}` | `{merr}` | {ok} |".format(
            id=case["id"],
            desc=case["desc"],
            brc=b_rc,
            mrc=m_rc,
            bout=_one_line(b_out),
            mout=_one_line(m_out),
            berr=_one_line(b_err),
            merr=_one_line(m_err),
            ok="ok" if ok else "mismatch",
        )
    )

now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
out = [
    "# Parameter Brace/Quote Edge Matrix",
    "",
    f"Generated: {now}",
    "Comparator: `bash --posix`",
    "Target: `mctash --posix`",
    "",
    "This is a focused parser/expansion edge corpus for `${...}` with mixed quote/brace content.",
    "",
    f"- Full parity rows: {full}/{len(CASES)}",
    "",
    "| Case | Intent | bash rc | mctash rc | bash stdout | mctash stdout | bash stderr | mctash stderr | Parity |",
    "|---|---|---:|---:|---|---|---|---|---|",
]
out.extend(rows)
out.append("")
out.append("## Notes")
out.append("")
out.append("- `malformed` rows are expected to error; parity requires matching error behavior class (rc+stderr), not exact wording.")
out.append("- This report is a parser/expansion roadmap input; it is intentionally narrow and pathological.")
out.append("")

REPORT.write_text("\n".join(out))
print(REPORT)
PY

echo "Wrote ${REPORT}"
