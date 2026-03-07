#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SpecPair:
    source_name: str
    source_url: str
    req_path: Path
    matrix_path: Path


SPECS = [
    SpecPair(
        source_name="bash-man",
        source_url="man bash",
        req_path=ROOT / "docs/specs/bash-man-requirements.tsv",
        matrix_path=ROOT / "docs/specs/bash-man-implementation-matrix.tsv",
    ),
    SpecPair(
        source_name="bash-posix-doc",
        source_url="https://tiswww.case.edu/php/chet/bash/POSIX",
        req_path=ROOT / "docs/specs/bash-posix-mode-requirements.tsv",
        matrix_path=ROOT / "docs/specs/bash-posix-mode-implementation-matrix.tsv",
    ),
    SpecPair(
        source_name="bash-compat-doc",
        source_url="https://tiswww.case.edu/php/chet/bash/COMPAT",
        req_path=ROOT / "docs/specs/bash-compat-deltas-requirements.tsv",
        matrix_path=ROOT / "docs/specs/bash-compat-deltas-implementation-matrix.tsv",
    ),
]

BUILTIN_NAMES = [
    "alias", "bg", "bind", "break", "caller", "cd", "command", "compgen", "complete",
    "compopt", "continue", "declare", "dirs", "disown", "echo", "enable", "eval", "exec", "exit",
    "export", "fc", "fg", "getopts", "hash", "help", "history", "jobs", "kill", "let", "local",
    "mapfile", "popd", "printf", "pushd", "pwd", "read", "readarray", "readonly", "return", "set",
    "shift", "shopt", "source", "suspend", "test", "times", "trap", "type", "typeset", "ulimit",
    "umask", "unalias", "unset", "wait",
]

TOPIC_PATTERNS = [
    ("syntax:parameter-expansion", [r"\$\{", r"parameter expansion"]),
    ("syntax:command-substitution", [r"\$\(", r"command substitution"]),
    ("syntax:arithmetic", [r"\$\(\(", r"\(\(", r"arithmetic"]),
    ("syntax:[[ ]]", [r"\[\[", r"conditional command"]),
    ("syntax:quoting", [r"quot", r"single quote", r"double-quoted"]),
    ("syntax:redirection", [r"redirection", r"here-doc", r"here-string"]),
    ("runtime:job-control", [r"\bjob", r"\bfg\b", r"\bbg\b", r"\bjobs\b"]),
    ("runtime:signals-traps", [r"\bsignal", r"\btrap\b", r"SIG[A-Z]+", r"\bSIGCHLD\b"]),
    ("runtime:history", [r"\bhistory\b", r"HIST", r"\bfc\b"]),
    ("runtime:startup", [r"POSIXLY_CORRECT", r"\$ENV", r"startup", r"invocation"]),
    ("runtime:locale", [r"locale", r"LC_", r"strcoll", r"collation"]),
    ("runtime:prompt", [r"\bPS1\b", r"\bPS2\b", r"prompt"]),
]

SPECIAL_BUILTIN_TOKENS = {
    "LBRACK": "[",
    "RBRACK": "]",
    "DOT": ".",
    "COLON": ":",
    "DASH": "-",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", errors="surrogateescape", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def source_ref(source: str, row: dict[str, str]) -> str:
    if source == "bash-man":
        return f"bash(1) section {row.get('bash_man_section', '').strip()}"
    if source == "bash-posix-doc":
        return f"bash/POSIX {row.get('source_section', '').strip()} item {row.get('source_item', '').strip()}"
    if source == "bash-compat-doc":
        return f"bash/COMPAT level {row.get('compat_level', '').strip()} item {row.get('item_index', '').strip()}"
    return source


def topic_for(record: dict[str, str]) -> str:
    req_id = record.get("req_id", "")
    feature = normalize(record.get("feature", ""))
    subcategory = normalize(record.get("subcategory", ""))

    m = re.search(r"C5\.BUILTIN\.([A-Z0-9_]+)", req_id)
    if m:
        token = m.group(1)
        builtin = SPECIAL_BUILTIN_TOKENS.get(token, token.lower())
        return f"builtin:{builtin}"

    m = re.search(r"C6\.VAR\.[A-Z0-9_]+\.([A-Z0-9_]+)$", req_id)
    if m:
        return f"var:{m.group(1)}"

    feature_l = feature.lower()
    quoted_tokens = re.findall(r"[`'‘’]([A-Za-z0-9_+./:@-]+)[`'‘’]", feature)
    for tok in quoted_tokens:
        low = tok.lower()
        if low in BUILTIN_NAMES:
            return f"builtin:{low}"

    m = re.search(r"\b([a-z][a-z0-9_+-]*)\s+builtin\b", feature_l)
    if m and m.group(1) in BUILTIN_NAMES:
        return f"builtin:{m.group(1)}"

    for name in BUILTIN_NAMES:
        if re.search(rf"\b{re.escape(name)}\b", feature_l):
            return f"builtin:{name}"

    for topic, pats in TOPIC_PATTERNS:
        for pat in pats:
            if re.search(pat, feature, re.IGNORECASE):
                return topic

    if subcategory:
        return f"subcategory:{subcategory}"
    return "misc:unclassified"


def notes_short(text: str, limit: int = 140) -> str:
    text = normalize(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def generate() -> int:
    combined: list[dict[str, str]] = []
    source_links: dict[str, str] = {}

    for spec in SPECS:
        req_rows = read_tsv(spec.req_path)
        matrix_rows = {row["req_id"]: row for row in read_tsv(spec.matrix_path)}
        source_links[spec.source_name] = spec.source_url

        for row in req_rows:
            rid = row["req_id"]
            mrow = matrix_rows.get(rid, {})
            rec = {
                "topic": "",
                "req_id": rid,
                "source": spec.source_name,
                "source_ref": source_ref(spec.source_name, row),
                "subcategory": normalize(row.get("subcategory", "")),
                "feature": normalize(row.get("feature", "")),
                "tests": normalize(mrow.get("tests", "")),
                "default": normalize(mrow.get("mctash_default", "")),
                "posix": normalize(mrow.get("mctash_posix", "")),
                "notes": normalize(mrow.get("notes", row.get("notes", ""))),
            }
            rec["topic"] = topic_for(rec)
            combined.append(rec)

    combined.sort(key=lambda r: (r["topic"], r["req_id"]))

    out_tsv = ROOT / "docs/specs/feature-index.tsv"
    out_md = ROOT / "docs/specs/feature-index.md"
    out_gap_tsv = ROOT / "docs/specs/feature-gap-board.tsv"
    out_gap_md = ROOT / "docs/specs/feature-gap-board.md"

    with out_tsv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "topic",
                "req_id",
                "source",
                "source_ref",
                "subcategory",
                "feature",
                "mctash_default",
                "mctash_posix",
                "tests",
                "notes",
            ]
        )
        for r in combined:
            writer.writerow(
                [
                    r["topic"],
                    r["req_id"],
                    r["source"],
                    r["source_ref"],
                    r["subcategory"],
                    r["feature"],
                    r["default"],
                    r["posix"],
                    r["tests"],
                    r["notes"],
                ]
            )

    def is_gap_status(v: str) -> bool:
        vv = (v or "").strip().lower()
        return vv not in ("", "covered")

    gap_rows = [r for r in combined if is_gap_status(r["default"]) or is_gap_status(r["posix"])]
    gap_rows.sort(key=lambda r: (r["topic"], r["req_id"]))

    with out_gap_tsv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "topic",
                "req_id",
                "source",
                "source_ref",
                "mctash_default",
                "mctash_posix",
                "tests",
                "feature",
                "notes",
            ]
        )
        for r in gap_rows:
            writer.writerow(
                [
                    r["topic"],
                    r["req_id"],
                    r["source"],
                    r["source_ref"],
                    r["default"],
                    r["posix"],
                    r["tests"],
                    r["feature"],
                    r["notes"],
                ]
            )

    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in combined:
        by_topic[r["topic"]].append(r)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: list[str] = []
    lines.append("# Feature Index")
    lines.append("")
    lines.append(f"Generated: {ts}")
    lines.append("")
    lines.append("Purpose: group requirement rows by feature/topic so design, implementation, and tests can be handled as coherent feature stories instead of row-by-row patches.")
    lines.append("")
    lines.append("Source matrices:")
    lines.append("")
    for src, url in sorted(source_links.items()):
        lines.append(f"- `{src}`: `{url}`")
    lines.append("- `docs/specs/bash-man-implementation-matrix.tsv`")
    lines.append("- `docs/specs/bash-posix-mode-implementation-matrix.tsv`")
    lines.append("- `docs/specs/bash-compat-deltas-implementation-matrix.tsv`")
    lines.append("")
    lines.append("## Topic Summary")
    lines.append("")
    lines.append("| Topic | Rows | Covered | Partial | Other |")
    lines.append("|---|---:|---:|---:|---:|")

    for topic in sorted(by_topic):
        rows = by_topic[topic]
        statuses = Counter((r["default"] or "unknown") for r in rows)
        covered = statuses.get("covered", 0)
        partial = statuses.get("partial", 0)
        other = len(rows) - covered - partial
        lines.append(f"| `{topic}` | {len(rows)} | {covered} | {partial} | {other} |")

    lines.append("")
    lines.append("## Feature Topics")
    lines.append("")

    for topic in sorted(by_topic):
        rows = by_topic[topic]
        lines.append(f"### `{topic}`")
        lines.append("")
        lines.append("| Req ID | Source | Source Ref | Status (default/posix) | Tests | Feature |")
        lines.append("|---|---|---|---|---|---|")
        for r in rows:
            status = f"{r['default'] or '-'} / {r['posix'] or '-'}"
            tests = r["tests"] or "-"
            lines.append(
                f"| `{r['req_id']}` | `{r['source']}` | {r['source_ref']} | `{status}` | `{tests}` | {r['feature']} |"
            )
        lines.append("")
        lines.append("Notes:")
        lines.append("")
        for r in rows[:8]:
            if r["notes"]:
                lines.append(f"- `{r['req_id']}`: {notes_short(r['notes'])}")
        if len(rows) > 8:
            lines.append(f"- (Plus {len(rows) - 8} additional row notes; see `docs/specs/feature-index.tsv`.)")
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    gap_by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in gap_rows:
        gap_by_topic[r["topic"]].append(r)

    glines: list[str] = []
    glines.append("# Feature Gap Board")
    glines.append("")
    glines.append(f"Generated: {ts}")
    glines.append("")
    glines.append("Purpose: implementation-first backlog grouped by feature topic (rows where either default or posix status is not `covered`).")
    glines.append("")
    glines.append("## Topic Backlog Summary")
    glines.append("")
    glines.append("| Topic | Gap Rows |")
    glines.append("|---|---:|")
    for topic in sorted(gap_by_topic):
        glines.append(f"| `{topic}` | {len(gap_by_topic[topic])} |")
    glines.append("")
    glines.append("## Gap Topics")
    glines.append("")
    for topic in sorted(gap_by_topic):
        rows = gap_by_topic[topic]
        glines.append(f"### `{topic}`")
        glines.append("")
        glines.append("| Req ID | Source | Status (default/posix) | Tests | Feature |")
        glines.append("|---|---|---|---|---|")
        for r in rows:
            status = f"{r['default'] or '-'} / {r['posix'] or '-'}"
            glines.append(
                f"| `{r['req_id']}` | `{r['source']}` | `{status}` | `{r['tests'] or '-'}` | {r['feature']} |"
            )
        glines.append("")

    out_gap_md.write_text("\n".join(glines), encoding="utf-8")
    print(f"wrote {out_tsv}")
    print(f"wrote {out_md}")
    print(f"wrote {out_gap_tsv}")
    print(f"wrote {out_gap_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate())
