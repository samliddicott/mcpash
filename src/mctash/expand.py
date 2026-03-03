from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple, Union

from .expand_legacy_markers import (
    ESCAPED_SLASH_MARK,
    QUOTED_EMPTY_MARK,
    contains_glob_meta,
    glob_pattern_display,
    glob_pattern_for_match,
    protect_glob_meta,
    unprotect_glob_meta,
)


@dataclass
class WordPart:
    kind: str  # LIT, PARAM, CMD, CMD_BQ, ARITH, BRACED
    value: str
    quoted: bool
    op: str | None = None
    arg: str | None = None


class PresplitFields(list):
    """A list of fields that must not be split again by IFS."""

    def __init__(self, values=None, lead_boundary: bool = False, trail_boundary: bool = False):
        super().__init__(values or [])
        self.lead_boundary = lead_boundary
        self.trail_boundary = trail_boundary


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
            if ch == "$" and i + 1 < len(text) and text[i + 1] == "'":
                flush(False)
                decoded, new_i = _parse_ansi_c_single(text, i)
                if new_i != i + 1:
                    parts.append(WordPart("LIT", decoded, quoted=True))
                    i = new_i
                    continue
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
                if text[i + 1] == "/":
                    # Preserve an explicit escaped slash (\ /) distinctly from
                    # plain quoted slashes so later pathname display can keep
                    # the backslash where ash does.
                    parts.append(WordPart("LIT", ESCAPED_SLASH_MARK, quoted=True))
                else:
                    parts.append(WordPart("LIT", text[i + 1], quoted=True))
                i += 2
                continue
            if ch == "`":
                flush(False)
                j = i + 1
                cmd: List[str] = []
                while j < len(text):
                    if text[j] == "\\" and j + 1 < len(text):
                        nxt = text[j + 1]
                        if nxt in ["\\", "`", "$", "\n"]:
                            cmd.append(nxt)
                            j += 2
                            continue
                        cmd.append("\\")
                        cmd.append(nxt)
                        j += 2
                        continue
                    if text[j] == "`":
                        break
                    cmd.append(text[j])
                    j += 1
                parts.append(WordPart("CMD_BQ", "".join(cmd), quoted=False))
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
                        nxt = text[j + 1]
                        if nxt in ["\\", "`", "$", '"', "\n"]:
                            cmd.append(nxt)
                            j += 2
                            continue
                        cmd.append("\\")
                        cmd.append(nxt)
                        j += 2
                        continue
                    if text[j] == "`":
                        break
                    cmd.append(text[j])
                    j += 1
                parts.append(WordPart("CMD_BQ", "".join(cmd), quoted=True))
                quote_has_parts = True
                i = j + 1 if j < len(text) and text[j] == "`" else j
                continue
            buf.append(ch)
            i += 1
            continue

    flush(mode != "plain")
    return parts


def _parse_ansi_c_single(text: str, start: int) -> Tuple[str, int]:
    if start + 1 >= len(text) or text[start] != "$" or text[start + 1] != "'":
        return "", start + 1
    i = start + 2
    out: List[str] = []
    while i < len(text):
        ch = text[i]
        if ch == "'":
            return "".join(out), i + 1
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "n":
                out.append("\n")
            elif nxt == "t":
                out.append("\t")
            elif nxt == "r":
                out.append("\r")
            elif nxt == "a":
                out.append("\a")
            elif nxt == "b":
                out.append("\b")
            elif nxt == "f":
                out.append("\f")
            elif nxt == "v":
                out.append("\v")
            elif nxt in ["\\", "'", '"']:
                out.append(nxt)
            elif nxt in "01234567":
                octal = nxt
                j = i + 2
                while j < len(text) and len(octal) < 3 and text[j] in "01234567":
                    octal += text[j]
                    j += 1
                code = int(octal, 8)
                if code != 0:
                    out.append(chr(code))
                i = j
                continue
            elif nxt == "x":
                hx = ""
                j = i + 2
                while j < len(text) and len(hx) < 2 and text[j] in "0123456789abcdefABCDEF":
                    hx += text[j]
                    j += 1
                if hx:
                    code = int(hx, 16)
                    if code != 0:
                        out.append(chr(code))
                    i = j
                    continue
                out.append("\\x")
            else:
                out.append("\\")
                out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out), start + 1


def _parse_dollar(text: str, i: int, quoted: bool) -> Tuple[WordPart, int]:
    if text.startswith("$((", i):
        content, end = _extract_balanced(text, i + 3, "))")
        return WordPart("ARITH", content, quoted), end
    if text.startswith("$(", i):
        content, end = _extract_balanced(text, i + 2, ")")
        return WordPart("CMD", content, quoted), end
    if text.startswith("${", i):
        end = _find_braced_end(text, i + 2)
        if end == -1:
            return WordPart("LIT", "$", quoted), i + 1
        inner = text[i + 2 : end]
        name, op, arg = _split_braced(inner)
        if name is None:
            return WordPart("BRACED", "", quoted, op="__invalid__", arg=inner), end + 1
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
    if closing == "))":
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
            if ch == "'":
                in_single = True
                i += 1
                continue
            if ch == '"':
                in_double = True
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text):
                i += 2
                continue
            if text.startswith("$((", i):
                depth += 1
                i += 3
                continue
            if ch == "(":
                paren_depth += 1
                i += 1
                continue
            if text.startswith("))", i):
                if depth > 1:
                    depth -= 1
                    i += 2
                    continue
                if paren_depth > 0:
                    paren_depth -= 1
                    i += 1
                    continue
                depth -= 1
                if depth == 0:
                    return text[start:i], i + 2
                i += 2
                continue
            if ch == ")" and paren_depth > 0:
                paren_depth -= 1
                i += 1
                continue
            i += 1
        return text[start:], len(text)
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
            if ch == "`":
                i += 1
                while i < len(text):
                    if text[i] == "\\" and i + 1 < len(text):
                        i += 2
                        continue
                    if text[i] == "`":
                        i += 1
                        break
                    i += 1
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
        if ch == "\\" and i + 1 < len(text):
            i += 2
            continue
        if ch == "`":
            i += 1
            while i < len(text):
                if text[i] == "\\" and i + 1 < len(text):
                    i += 2
                    continue
                if text[i] == "`":
                    i += 1
                    break
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
        if closing == ")":
            if ch == "(":
                paren_depth += 1
                i += 1
                continue
            if ch == ")":
                if paren_depth > 0:
                    paren_depth -= 1
                    i += 1
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


def _find_braced_end(text: str, start: int) -> int:
    depth = 1
    i = start
    in_single = False
    in_double = False
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
            if ch == "`":
                i += 1
                while i < len(text):
                    if text[i] == "\\" and i + 1 < len(text):
                        i += 2
                        continue
                    if text[i] == "`":
                        i += 1
                        break
                    i += 1
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
        if ch == "\\" and i + 1 < len(text):
            i += 2
            continue
        if text.startswith("$((", i):
            _, i = _extract_balanced(text, i + 3, "))")
            continue
        if text.startswith("$(", i):
            _, i = _extract_balanced(text, i + 2, ")")
            continue
        if text.startswith("${", i):
            depth += 1
            i += 2
            continue
        if ch == "`":
            i += 1
            while i < len(text):
                if text[i] == "\\" and i + 1 < len(text):
                    i += 2
                    continue
                if text[i] == "`":
                    i += 1
                    break
                i += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                return i
            i += 1
            continue
        i += 1
    return -1


def _split_braced(inner: str) -> Tuple[str | None, str | None, str | None]:
    def _consume_subscript(text: str, j: int) -> int:
        if j >= len(text) or text[j] != "[":
            return j
        k = j + 1
        while k < len(text) and text[k] != "]":
            k += 1
        if k >= len(text):
            return j
        return k + 1

    def _parse_param_name(text: str) -> Tuple[str | None, int]:
        if not text:
            return None, 0
        if text[0] in "@*#?$!-":
            return text[0], 1
        if text[0].isdigit():
            return text[0], 1
        if text[0].isalpha() or text[0] == "_":
            j = 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            j2 = _consume_subscript(text, j)
            if j2 != j:
                j = j2
            return text[:j], j
        return None, 0

    if not inner:
        return None, None, None
    if inner.startswith("!"):
        rest_inner = inner[1:]
        if not rest_inner or not (rest_inner[0].isalpha() or rest_inner[0] == "_"):
            return None, None, None
        j = 1
        while j < len(rest_inner) and (rest_inner[j].isalnum() or rest_inner[j] == "_"):
            j += 1
        base = rest_inner[:j]
        rest = rest_inner[j:]
        if rest == "[@]":
            return base, "__keys__", "@"
        if rest == "[*]":
            return base, "__keys__", "*"
        return None, None, None
    if inner.startswith("#") and len(inner) > 1:
        len_name, used = _parse_param_name(inner[1:])
        if len_name is not None and used == len(inner) - 1:
            return len_name, "__len__", None
    i = 0
    if inner[0] in "@*#?$!-":
        name = inner[0]
        i = 1
    elif inner[0].isdigit():
        name = inner[0]
        i = 1
    else:
        name_chars: List[str] = []
        while i < len(inner) and (inner[i].isalnum() or inner[i] == "_"):
            name_chars.append(inner[i])
            i += 1
        if not name_chars:
            return None, None, None
        if i < len(inner) and inner[i] == "[":
            j = _consume_subscript(inner, i)
            if j == i:
                return None, None, None
            name = "".join(name_chars) + inner[i:j]
            i = j
        else:
            name = "".join(name_chars)
    if i >= len(inner):
        return name, None, None
    if inner[i] == ":" and (i + 1 >= len(inner) or inner[i + 1] not in "-=?+"):
        return name, ":substr", inner[i + 1 :]
    if inner[i] == "/":
        return name, "/", inner[i + 1 :]
    two_char_ops = {":-", ":=", ":?", ":+", "##", "%%"}
    if i + 1 < len(inner) and inner[i : i + 2] in two_char_ops:
        op = inner[i : i + 2]
        return name, op, inner[i + 2 :]
    if inner[i] in ["-", "=", "?", "#", "%", "+"]:
        op = inner[i]
        return name, op, inner[i + 1 :]
    return None, None, None


def expand_word(
    text: str,
    get_param: Callable[[str, bool], Union[str, List[str]]],
    get_param_braced: Callable[[str, str | None, str | None, bool], Union[str, List[str]]],
    eval_cmd: Callable[[str, bool], str],
    eval_arith: Callable[[str], str],
    split_ifs: Callable[[str], List[str]],
    glob_field: Callable[[str], List[str]],
    unprotect_literals: bool = True,
    split_unquoted_literals: bool = False,
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
            if part.quoted and value == "":
                # Preserve explicit quoted-empty literals as word anchors
                # around later unquoted field splitting.
                value = QUOTED_EMPTY_MARK
        elif part.kind == "PARAM":
            value = get_param(part.value, part.quoted)
        elif part.kind == "BRACED":
            value = get_param_braced(part.value, part.op, part.arg, part.quoted)
        elif part.kind == "CMD":
            value = eval_cmd(part.value, False)
        elif part.kind == "CMD_BQ":
            value = eval_cmd(part.value, True)
        elif part.kind == "ARITH":
            value = eval_arith(part.value)
        else:
            value = part.value

        is_quoted_list_splat = (
            isinstance(value, list)
            and part.quoted
            and (
                (part.kind == "PARAM" and part.value == "@")
                or (part.kind == "BRACED" and part.value.endswith("[@]"))
            )
        )
        if is_quoted_list_splat:
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

        if part.quoted:
            if isinstance(value, list):
                value = [protect_glob_meta(v) for v in value]
            else:
                value = protect_glob_meta(value)

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
                    all_parts: List[str] = []
                    saw_delim_only = False
                    if isinstance(value, PresplitFields):
                        if value.lead_boundary and (f != "" or q):
                            new_fields.append((f, q, False, gm))
                            f = ""
                        all_parts.extend(list(value))
                    else:
                        for v in value:
                            pieces = split_ifs(v)
                            if not pieces:
                                if v != "":
                                    saw_delim_only = True
                                continue
                            all_parts.extend(pieces)
                    if not all_parts:
                        if saw_delim_only:
                            if f != "" or q:
                                new_fields.append((f, q, False, gm))
                            new_fields.append(("", q, True, False))
                        else:
                            new_fields.append((f, q, True, gm))
                        continue
                    if saw_delim_only and (f != "" or q):
                        new_fields.append((f, q, False, gm))
                        f = ""
                    if len(all_parts) == 1:
                        p = all_parts[0]
                        is_trail = isinstance(value, PresplitFields) and value.trail_boundary and idx < len(parts) - 1
                        new_fields.append((f + p, q, (not is_trail), gm or has_glob_meta(p)))
                        if is_trail:
                            new_fields.append(("", q, True, False))
                    else:
                        first = all_parts[0]
                        new_fields.append((f + first, q, False, gm or has_glob_meta(first)))
                        for p in all_parts[1:-1]:
                            new_fields.append((p, q, False, has_glob_meta(p)))
                        last = all_parts[-1]
                        is_trail = isinstance(value, PresplitFields) and value.trail_boundary and idx < len(parts) - 1
                        new_fields.append((last, q, (not is_trail), has_glob_meta(last)))
                        if is_trail:
                            new_fields.append(("", q, True, False))
            fields = new_fields
            continue

        if part.kind == "LIT" and (not part.quoted) and (not split_unquoted_literals):
            fields = [
                (f + value, q, active, gm or has_glob_meta(value)) if active else (f, q, active, gm)
                for f, q, active, gm in fields
            ]
            continue

        if part.quoted:
            fields = [
                (f + value, True or q, active, gm) if active else (f, True or q, active, gm)
                for f, q, active, gm in fields
            ]
        else:
            pieces = split_ifs(value)
            if not pieces:
                if value != "":
                    new_fields = []
                    for f, q, active, gm in fields:
                        if not active:
                            new_fields.append((f, q, active, gm))
                            continue
                        # Delimiter-only text still creates a field boundary.
                        if f != "" or q:
                            new_fields.append((f, q, False, gm))
                        # Trailing IFS-whitespace delimiter should not force an
                        # extra empty field at end-of-word.
                        if idx < len(parts) - 1 or (f != "" or not q):
                            new_fields.append(("", q, True, False))
                    fields = new_fields
                else:
                    fields = [(f, q, active, gm) for f, q, active, gm in fields]
            else:
                new_fields = []
                for f, q, active, gm in fields:
                    if not active:
                        new_fields.append((f, q, active, gm))
                        continue
                    if len(pieces) == 1:
                        p = pieces[0]
                        lead_delim = not value.startswith(p)
                        trail_delim = not value.endswith(p)
                        if lead_delim and (f != "" or q):
                            new_fields.append((f, q, False, gm))
                            f = ""
                        if trail_delim and idx < len(parts) - 1:
                            new_fields.append((f + p, q, False, gm or has_glob_meta(p)))
                            new_fields.append(("", q, True, False))
                        else:
                            new_fields.append((f + p, q, True, gm or has_glob_meta(p)))
                    else:
                        first = pieces[0]
                        lead_delim = not value.startswith(first)
                        trail_delim = not value.endswith(pieces[-1])
                        if lead_delim and (f != "" or q):
                            new_fields.append((f, q, False, gm))
                            f = ""
                        new_fields.append((f + first, q, False, gm or has_glob_meta(first)))
                        for p in pieces[1:-1]:
                            new_fields.append((p, q, False, has_glob_meta(p)))
                        last = pieces[-1]
                        if trail_delim and idx < len(parts) - 1:
                            new_fields.append((last, q, False, has_glob_meta(last)))
                            new_fields.append(("", q, True, False))
                        else:
                            new_fields.append((last, q, True, has_glob_meta(last)))
                fields = new_fields

    expanded: List[str] = []
    for f, quoted, _, has_meta in fields:
        rendered = unprotect_glob_meta(f) if unprotect_literals else f
        rendered = rendered.replace(QUOTED_EMPTY_MARK, "")
        # Globbing is driven by unquoted meta presence, not by whether any
        # quoted fragments contributed to the same output field.
        if has_meta or not quoted:
            g = f if unprotect_literals else rendered
            g = g.replace(QUOTED_EMPTY_MARK, "")
            expanded.extend(glob_field(g))
        else:
            expanded.append(rendered)
    return expanded
