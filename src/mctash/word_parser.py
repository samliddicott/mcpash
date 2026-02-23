from __future__ import annotations

from .lst_nodes import (
    LstArithSubPart,
    LstBracedVarSubPart,
    LstCommandSubPart,
    LstDoubleQuotedPart,
    LstLiteralPart,
    LstParamPart,
    LstSingleQuotedPart,
    LstWord,
    LstWordPart,
)


def parse_word(
    text: str,
    *,
    line: int | None = None,
    col: int | None = None,
    index: int | None = None,
) -> LstWord:
    parts = _parse_parts(text, in_double=False)
    if not parts:
        parts = [LstLiteralPart("")]
    return LstWord(parts=parts, line=line, col=col, length=len(text), index=index)


def _parse_param(text: str, start: int) -> tuple[str | None, int]:
    if start + 1 >= len(text):
        return None, 1
    nxt = text[start + 1]
    if nxt in "@*#?$!-":
        return nxt, 2
    if nxt.isdigit():
        return nxt, 2
    if text[start + 1] == "{":
        end = text.find("}", start + 2)
        if end == -1:
            return None, 1
        name = text[start + 2 : end]
        if not _valid_param_name(name):
            return None, 1
        return name, end - start + 1
    i = start + 1
    name_chars: list[str] = []
    while i < len(text) and (text[i].isalnum() or text[i] == "_"):
        name_chars.append(text[i])
        i += 1
    if not name_chars:
        return None, 1
    return "".join(name_chars), i - start


def _valid_name(name: str) -> bool:
    if not name:
        return False
    if not (name[0].isalpha() or name[0] == "_"):
        return False
    return all(ch.isalnum() or ch == "_" for ch in name)


def _valid_param_name(name: str) -> bool:
    if not name:
        return False
    if len(name) == 1 and name in "@*#?$!-":
        return True
    if name.isdigit():
        return True
    return _valid_name(name)


def _parse_parts(text: str, in_double: bool) -> list[LstWordPart]:
    parts: list[LstWordPart] = []
    buf: list[str] = []
    i = 0

    def flush_literal() -> None:
        nonlocal buf
        if buf:
            parts.append(LstLiteralPart("".join(buf)))
            buf = []

    while i < len(text):
        ch = text[i]
        if not in_double and ch == "'":
            flush_literal()
            end = text.find("'", i + 1)
            if end == -1:
                parts.append(LstLiteralPart(text[i:]))
                return parts
            parts.append(LstSingleQuotedPart(text[i + 1 : end]))
            i = end + 1
            continue
        if not in_double and ch == '"':
            flush_literal()
            end = _find_matching_quote(text, i + 1)
            if end == -1:
                parts.append(LstLiteralPart(text[i:]))
                return parts
            inner = text[i + 1 : end]
            inner_parts = _parse_parts(inner, in_double=True)
            parts.append(LstDoubleQuotedPart(inner_parts))
            i = end + 1
            continue
        if ch == "`":
            flush_literal()
            end = _find_backtick(text, i + 1)
            if end == -1:
                parts.append(LstLiteralPart(text[i:]))
                return parts
            inner = text[i + 1 : end]
            parts.append(LstCommandSubPart(inner))
            i = end + 1
            continue
        if ch == "$":
            if text.startswith("${", i):
                part, consumed = _parse_braced_var(text, i)
                if part is not None:
                    flush_literal()
                    parts.append(part)
                    i += consumed
                    continue
            if text.startswith("$((", i):
                sub, consumed = _parse_arith_sub(text, i)
                if sub is not None:
                    flush_literal()
                    parts.append(LstArithSubPart(sub))
                    i += consumed
                    continue
            if text.startswith("$(", i):
                sub, consumed = _parse_command_sub(text, i)
                if sub is not None:
                    flush_literal()
                    parts.append(LstCommandSubPart(sub))
                    i += consumed
                    continue
            name, consumed = _parse_param(text, i)
            if name is not None:
                flush_literal()
                parts.append(LstParamPart(name=name))
                i += consumed
                continue
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if in_double and nxt not in ['$', '"', "\\", "`", "\n"]:
                buf.append(ch)
                i += 1
                continue
            buf.append(nxt)
            i += 2
            continue
        buf.append(ch)
        i += 1
    flush_literal()
    return parts


def _find_matching_quote(text: str, start: int) -> int:
    i = start
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == '"':
            return i
        i += 1
    return -1


def _find_backtick(text: str, start: int) -> int:
    i = start
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "`":
            return i
        i += 1
    return -1


def _parse_command_sub(text: str, start: int) -> tuple[str | None, int]:
    if not text.startswith("$(", start):
        return None, 1
    i = start + 2
    depth = 1
    while i < len(text):
        if text.startswith("$(", i):
            depth += 1
            i += 2
            continue
        if text[i] == "(":
            depth += 1
            i += 1
            continue
        if text[i] == ")":
            depth -= 1
            i += 1
            if depth == 0:
                inner = text[start + 2 : i - 1]
                return inner, i - start
            continue
        i += 1
    return None, 1


def _parse_arith_sub(text: str, start: int) -> tuple[str | None, int]:
    if not text.startswith("$((", start):
        return None, 1
    i = start + 3
    depth = 1
    while i < len(text):
        if text.startswith("((", i):
            depth += 1
            i += 2
            continue
        if text.startswith("))", i):
            depth -= 1
            i += 2
            if depth == 0:
                inner = text[start + 3 : i - 2]
                return inner, i - start
            continue
        i += 1
    return None, 1


def _parse_braced_var(text: str, start: int) -> tuple[LstWordPart | None, int]:
    if not text.startswith("${", start):
        return None, 1
    end = text.find("}", start + 2)
    if end == -1:
        return None, 1
    inner = text[start + 2 : end]
    name, op, arg = _split_braced_var(inner)
    if name is None:
        return None, 1
    if op is None:
        return LstBracedVarSubPart(name=name), end - start + 1
    arg_word = parse_word(arg) if arg is not None else None
    return LstBracedVarSubPart(name=name, op=op, arg=arg_word), end - start + 1


def _split_braced_var(inner: str) -> tuple[str | None, str | None, str | None]:
    i = 0
    if not inner:
        return None, None, None
    if inner.startswith("#") and len(inner) > 1:
        name = inner[1:]
        if _valid_param_name(name):
            return name, "__len__", None
    if inner[0] in "@*#?$!-" and len(inner) >= 1:
        name = inner[0]
        i = 1
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
    name_chars: list[str] = []
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
    if inner[i] in ["-", "=", "?", "#", "%"]:
        op = inner[i]
        return name, op, inner[i + 1 :]
    return name, None, None
