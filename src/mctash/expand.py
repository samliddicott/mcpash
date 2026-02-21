from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple


@dataclass
class WordPart:
    kind: str  # LIT, PARAM, CMD, ARITH
    value: str
    quoted: bool


def parse_word_parts(text: str) -> List[WordPart]:
    parts: List[WordPart] = []
    buf: List[str] = []
    i = 0
    mode = "plain"

    def flush(quoted: bool) -> None:
        nonlocal buf
        if buf:
            parts.append(WordPart("LIT", "".join(buf), quoted))
            buf = []

    while i < len(text):
        ch = text[i]
        if mode == "plain":
            if ch == "'":
                flush(False)
                mode = "single"
                i += 1
                continue
            if ch == '"':
                flush(False)
                mode = "double"
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text):
                i += 1
                buf.append(text[i])
                i += 1
                continue
            if ch == "$":
                flush(False)
                part, i = _parse_dollar(text, i, quoted=False)
                parts.append(part)
                continue
            buf.append(ch)
            i += 1
            continue
        if mode == "single":
            if ch == "'":
                flush(True)
                mode = "plain"
                i += 1
                continue
            buf.append(ch)
            i += 1
            continue
        if mode == "double":
            if ch == '"':
                flush(True)
                mode = "plain"
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text) and text[i + 1] in ['"', "\\", "$", "`"]:
                i += 1
                buf.append(text[i])
                i += 1
                continue
            if ch == "$":
                flush(True)
                part, i = _parse_dollar(text, i, quoted=True)
                parts.append(part)
                continue
            buf.append(ch)
            i += 1
            continue

    flush(mode != "plain")
    return parts


def _parse_dollar(text: str, i: int, quoted: bool) -> Tuple[WordPart, int]:
    if text.startswith("$((", i):
        content, end = _extract_balanced(text, i + 3, "))")
        return WordPart("ARITH", content, quoted), end
    if text.startswith("$(", i):
        content, end = _extract_balanced(text, i + 2, ")")
        return WordPart("CMD", content, quoted), end
    if text.startswith("${", i):
        end = text.find("}", i + 2)
        if end == -1:
            return WordPart("LIT", "$", quoted), i + 1
        return WordPart("PARAM", text[i + 2 : end], quoted), end + 1
    if i + 1 < len(text):
        ch = text[i + 1]
        if ch in "#@*":
            return WordPart("PARAM", ch, quoted), i + 2
        if ch.isdigit():
            return WordPart("PARAM", ch, quoted), i + 2
        if ch.isalpha() or ch == "_":
            j = i + 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            return WordPart("PARAM", text[i + 1 : j], quoted), j
    return WordPart("LIT", "$", quoted), i + 1


def _extract_balanced(text: str, start: int, closing: str) -> Tuple[str, int]:
    depth = 1
    i = start
    while i < len(text):
        if text.startswith("$((", i):
            depth += 1
            i += 3
            continue
        if text.startswith("$(", i):
            depth += 1
            i += 2
            continue
        if text.startswith(closing, i):
            depth -= 1
            if depth == 0:
                return text[start:i], i + len(closing)
            i += len(closing)
            continue
        i += 1
    return text[start:], len(text)


def expand_word(
    text: str,
    get_param: Callable[[str, bool], str],
    eval_cmd: Callable[[str], str],
    eval_arith: Callable[[str], str],
    split_ifs: Callable[[str], List[str]],
    glob_field: Callable[[str], List[str]],
) -> List[str]:
    parts = parse_word_parts(text)
    fields: List[Tuple[str, bool]] = [("", False)]
    for part in parts:
        if part.kind == "LIT":
            value = part.value
        elif part.kind == "PARAM":
            value = get_param(part.value, part.quoted)
        elif part.kind == "CMD":
            value = eval_cmd(part.value)
        elif part.kind == "ARITH":
            value = eval_arith(part.value)
        else:
            value = part.value

        if part.quoted:
            fields = [(f + value, True or q) for f, q in fields]
        else:
            pieces = split_ifs(value)
            if not pieces:
                fields = [(f, q) for f, q in fields]
            else:
                new_fields: List[Tuple[str, bool]] = []
                for f, q in fields:
                    for p in pieces:
                        new_fields.append((f + p, q))
                fields = new_fields

    expanded: List[str] = []
    for f, quoted in fields:
        if quoted:
            expanded.append(f)
        else:
            expanded.extend(glob_field(f))
    return expanded
