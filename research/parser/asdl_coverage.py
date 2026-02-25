from __future__ import annotations

import re
from pathlib import Path

ASDL_PATH = Path("research/parser/osh_syntax/frontend.syntax.asdl")
REPORT_PATH = Path("research/parser/asdl_coverage_report.md")
CHECKLIST_PATH = Path("docs/grammar-production-checklist.md")

CHECKLIST_LINKS = {
    "word_part": ["`docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`"],
    "word": ["`docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`"],
    "command": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "redir_param": [
        "`docs/grammar-production-checklist.md#grammar-families`",
        "`docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`",
    ],
    "redir_loc": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "assign_op": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "arith_expr": ["`docs/grammar-production-checklist.md#word-level-grammar-sub-checklist`"],
    "bool_expr": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "condition": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "case_arg": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "pat": ["`docs/grammar-production-checklist.md#grammar-families`"],
    "for_iter": ["`docs/grammar-production-checklist.md#grammar-families`"],
}


def main() -> None:
    text = ASDL_PATH.read_text(encoding="utf-8")
    sections = {
        "word_part": extract_variants(text, "word_part"),
        "command": extract_variants(text, "command"),
        "redir_param": extract_variants(text, "redir_param"),
        "redir_loc": extract_variants(text, "redir_loc"),
        "assign_op": extract_variants(text, "assign_op"),
        "arith_expr": extract_variants(text, "arith_expr"),
        "bool_expr": extract_variants(text, "bool_expr"),
        "condition": extract_variants(text, "condition"),
        "case_arg": extract_variants(text, "case_arg"),
        "pat": extract_variants(text, "pat"),
        "for_iter": extract_variants(text, "for_iter"),
        "word": extract_variants(text, "word"),
    }

    implemented = {
        "word_part": {
            "Literal",
            "SingleQuoted",
            "DoubleQuoted",
            "SimpleVarSub",
            "BracedVarSub",
            "CommandSub",
            "ArithSub",
        },
        "command": {
            "Simple",
            "Pipeline",
            "AndOr",
            "BraceGroup",
            "Subshell",
            "If",
            "Case",
            "ShFunction",
            "CommandList",
            "ForEach",
            "WhileUntil",
            "Redirect",
            "ShAssignment",
            "ControlFlow",
            "Sentence",
        },
        "redir_param": {"Word", "HereDoc"},
        "redir_loc": {"Fd"},
        "word": {"Compound"},
    }

    lines = ["# ASDL Coverage Report", ""]
    lines.append(f"Source: `{ASDL_PATH}`")
    lines.append("")

    for section, variants in sections.items():
        lines.append(f"## {section}")
        if not variants:
            lines.append("(none)")
            lines.append("")
            continue
        implemented_count = 0
        missing_count = 0
        for name in variants:
            status = "missing"
            if name in implemented.get(section, set()):
                status = "implemented"
                implemented_count += 1
            else:
                missing_count += 1
            lines.append(f"- `{name}`: {status}")
        lines.append("")
        lines.append(
            f"Summary: implemented `{implemented_count}`, missing `{missing_count}`."
        )
        links = CHECKLIST_LINKS.get(section, [])
        if links:
            lines.append("Checklist links:")
            for link in links:
                lines.append(f"- {link}")
        else:
            lines.append(
                f"Checklist links: add mapping in `{CHECKLIST_PATH}` / `research/parser/asdl_coverage.py`."
            )
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def extract_variants(text: str, type_name: str) -> list[str]:
    lines = text.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().startswith(f"{type_name} ="):
            rhs = line.split("=", 1)[1].strip()
            if rhs:
                variants = []
                for part in rhs.split("|"):
                    name = re.split(r"[\s(]", part.strip(), 1)[0]
                    name = name.replace("%", "").strip()
                    if name:
                        variants.append(name)
                if variants:
                    return variants
            start_idx = idx + 1
            break
    if start_idx is None:
        return []
    lines = lines[start_idx:]
    variants: list[str] = []
    first_variant = True
    for line in lines:
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=", line):
            break
        if not line.startswith(" "):
            break
        chunk = line.strip()
        if chunk.startswith("|"):
            chunk = chunk[1:].strip()
        elif not first_variant:
            continue
        first_variant = False
        name = re.split(r"[\s(]", chunk, 1)[0]
        name = name.replace("%", "").strip()
        variants.append(name)
    return variants


if __name__ == "__main__":
    main()
