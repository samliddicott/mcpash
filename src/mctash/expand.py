from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple, Union


@dataclass
class WordPart:
    kind: str  # LIT, PARAM, CMD, ARITH, BRACED
    value: str
    quoted: bool
    op: str | None = None
    arg: str | None = None


def parse_word_parts(text: str) -> List[WordPart]:
    parts: List[WordPart] = []
    buf: List[str] = []
    i = 0
    mode = "plain"
    quote_has_parts = False

    def flush(quoted: bool, force: bool = False) -> None:
        nonlocal buf
        if buf or force:
            parts.append(WordPart("LIT", "".join(buf), quoted))
            buf = []

    while i < len(text):
        ch = text[i]
        if mode == "plain":
            if ch == "'":
                flush(False)
                mode = "single"
                quote_has_parts = False
                i += 1
                continue
            if ch == '"':
                flush(False)
                mode = "double"
                quote_has_parts = False
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text):
                if text[i + 1] == "\n":
                    i += 2
                    continue
                flush(False)
                parts.append(WordPart("LIT", text[i + 1], quoted=True))
                i += 2
                continue
            if ch == "`":
                flush(False)
                j = i + 1
                cmd: List[str] = []
                while j < len(text):
                    if text[j] == "\\" and j + 1 < len(text):
                        cmd.append(text[j + 1])
                        j += 2
                        continue
                    if text[j] == "`":
                        break
                    cmd.append(text[j])
                    j += 1
                parts.append(WordPart("CMD", "".join(cmd), quoted=False))
                i = j + 1 if j < len(text) and text[j] == "`" else j
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
                if buf:
                    flush(True)
                    quote_has_parts = True
                elif not quote_has_parts:
                    flush(True, force=True)
                mode = "plain"
                i += 1
                continue
            buf.append(ch)
            i += 1
            continue
        if mode == "double":
            if ch == '"':
                if buf:
                    flush(True)
                    quote_has_parts = True
                elif not quote_has_parts:
                    flush(True, force=True)
                mode = "plain"
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text) and text[i + 1] in ['"', "\\", "$", "`"]:
                i += 1
                buf.append(text[i])
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text) and text[i + 1] == "\n":
                i += 2
                continue
            if ch == "$":
                flush(True)
                part, i = _parse_dollar(text, i, quoted=True)
                parts.append(part)
                quote_has_parts = True
                continue
            if ch == "`":
                flush(True)
                j = i + 1
                cmd: List[str] = []
                while j < len(text):
                    if text[j] == "\\" and j + 1 < len(text):
                        cmd.append(text[j + 1])
                        j += 2
                        continue
                    if text[j] == "`":
                        break
                    cmd.append(text[j])
                    j += 1
                parts.append(WordPart("CMD", "".join(cmd), quoted=True))
                quote_has_parts = True
                i = j + 1 if j < len(text) and text[j] == "`" else j
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
        inner = text[i + 2 : end]
        if inner.startswith("#") and len(inner) > 1:
            name = inner[1:]
            return WordPart("BRACED", name, quoted, op="__len__", arg=None), end + 1
        name, op, arg = _split_braced(inner)
        if name is None:
            return WordPart("LIT", "$", quoted), i + 1
        return WordPart("BRACED", name, quoted, op=op, arg=arg), end + 1
    if i + 1 < len(text):
        ch = text[i + 1]
        if ch in "#@*?$!-":
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
    in_single = False
    in_double = False
    paren_depth = 0
    while i < len(text):
        ch = text[i]
        if in_single:
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if ch == "\\" and i + 1 < len(text):
                i += 2
                continue
            if ch == '"':
                in_double = False
                i += 1
                continue
            i += 1
            continue
        if ch == "'":
            in_single = True
            i += 1
            continue
        if ch == '"':
            in_double = True
            i += 1
            continue
        if text.startswith("$((", i):
            depth += 1
            i += 3
            continue
        if text.startswith("$(", i):
            depth += 1
            i += 2
            continue
        if closing == "))":
            if ch == "(":
                paren_depth += 1
                i += 1
                continue
            if ch == ")":
                if paren_depth > 0:
                    paren_depth -= 1
                    i += 1
                    continue
        if text.startswith(closing, i):
            depth -= 1
            if depth == 0:
                return text[start:i], i + len(closing)
            i += len(closing)
            continue
        i += 1
    return text[start:], len(text)


def _split_braced(inner: str) -> Tuple[str | None, str | None, str | None]:
    if not inner:
        return None, None, None
    i = 0
    name_chars: List[str] = []
    while i < len(inner) and (inner[i].isalnum() or inner[i] == "_"):
        name_chars.append(inner[i])
        i += 1
    if not name_chars:
        return None, None, None
    name = "".join(name_chars)
    if i >= len(inner):
        return name, None, None
    two_char_ops = {":-", ":=", ":?", ":+", "##", "%%"}
    if i + 1 < len(inner) and inner[i : i + 2] in two_char_ops:
        op = inner[i : i + 2]
        return name, op, inner[i + 2 :]
    if inner[i] in ["-", "=", "?", "#", "%", "+"]:
        op = inner[i]
        return name, op, inner[i + 1 :]
    return name, None, None


def expand_word(
    text: str,
    get_param: Callable[[str, bool], Union[str, List[str]]],
    get_param_braced: Callable[[str, str | None, str | None, bool], Union[str, List[str]]],
    eval_cmd: Callable[[str], str],
    eval_arith: Callable[[str], str],
    split_ifs: Callable[[str], List[str]],
    glob_field: Callable[[str], List[str]],
) -> List[str]:
    parts = parse_word_parts(text)
    # field tuple: (text, quoted_for_split, active, has_unquoted_glob_meta)
    # active=False means later word parts shouldn't be appended to this field.
    fields: List[Tuple[str, bool, bool, bool]] = [("", False, True, False)]

    def has_glob_meta(s: str) -> bool:
        return any(ch in s for ch in ["*", "?", "["])
    for idx, part in enumerate(parts):
        if part.kind == "LIT":
            value: Union[str, List[str]] = part.value
        elif part.kind == "PARAM":
            value = get_param(part.value, part.quoted)
        elif part.kind == "BRACED":
            value = get_param_braced(part.value, part.op, part.arg, part.quoted)
        elif part.kind == "CMD":
            value = eval_cmd(part.value)
        elif part.kind == "ARITH":
            value = eval_arith(part.value)
        else:
            value = part.value

        if part.kind == "PARAM" and part.value == "@" and part.quoted and isinstance(value, list):
            new_fields: List[Tuple[str, bool, bool, bool]] = []
            for f, q, active, gm in fields:
                if not active:
                    new_fields.append((f, q, active, gm))
                    continue
                if not value:
                    if f == "" and idx == len(parts) - 1 and not q:
                        continue
                    new_fields.append((f, True or q, True, gm))
                    continue
                if len(value) == 1:
                    new_fields.append((f + value[0], True or q, True, gm))
                    continue
                new_fields.append((f + value[0], True or q, False, gm))
                for v in value[1:-1]:
                    new_fields.append((v, True, False, False))
                new_fields.append((value[-1], True, True, False))
            fields = new_fields
            continue

        if isinstance(value, list):
            new_fields = []
            if part.quoted:
                for f, q, active, gm in fields:
                    if not active:
                        new_fields.append((f, q, active, gm))
                        continue
                    for v in value:
                        new_fields.append((f + v, True or q, True, gm))
            else:
                for f, q, active, gm in fields:
                    if not active:
                        new_fields.append((f, q, active, gm))
                        continue
                    for v in value:
                        pieces = split_ifs(v)
                        if not pieces:
                            new_fields.append((f, q, True, gm))
                        else:
                            for p in pieces:
                                new_fields.append((f + p, q, True, gm or has_glob_meta(p)))
            fields = new_fields
            continue

        if part.quoted:
            fields = [
                (f + value, True or q, active, gm) if active else (f, True or q, active, gm)
                for f, q, active, gm in fields
            ]
        else:
            pieces = split_ifs(value)
            if not pieces:
                fields = [(f, q, active, gm) for f, q, active, gm in fields]
            else:
                new_fields = []
                for f, q, active, gm in fields:
                    if not active:
                        new_fields.append((f, q, active, gm))
                        continue
                    for p in pieces:
                        new_fields.append((f + p, q, True, gm or has_glob_meta(p)))
                fields = new_fields

    expanded: List[str] = []
    for f, quoted, _, has_meta in fields:
        if has_meta:
            expanded.extend(glob_field(f))
        else:
            expanded.append(f)
    return expanded
