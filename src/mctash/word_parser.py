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
        if not in_double and ch == "$" and i + 1 < len(text) and text[i + 1] == "'":
            flush_literal()
            end = _find_ansi_c_single_quote_end(text, i + 2)
            if end == -1:
                parts.append(LstLiteralPart(text[i:]))
                return parts
            parts.append(LstLiteralPart("$"))
            parts.append(LstSingleQuotedPart(text[i + 2 : end]))
            i = end + 1
            continue
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
            inner = _decode_backtick_inner(text[i + 1 : end], in_double=in_double)
            parts.append(LstCommandSubPart(inner, style="backtick"))
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
                if sub is not None and _looks_like_arith_expr(sub):
                    flush_literal()
                    parts.append(LstArithSubPart(sub))
                    i += consumed
                    continue
            if text.startswith("$(", i):
                sub, consumed = _parse_command_sub(text, i)
                if sub is not None:
                    flush_literal()
                    parts.append(LstCommandSubPart(sub, style="dollar"))
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
            if nxt == "\n":
                i += 2
                continue
            if in_double and nxt not in ['$', '"', "\\", "`", "\n"]:
                buf.append(ch)
                i += 1
                continue
            buf.append("\\")
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
        if text.startswith("${", i):
            end = _find_matching_brace(text, i + 2)
            if end == -1:
                return -1
            i = end + 1
            continue
        if text.startswith("$((", i):
            sub, consumed = _parse_arith_sub(text, i)
            if sub is None:
                return -1
            i += consumed
            continue
        if text.startswith("$(", i):
            sub, consumed = _parse_command_sub(text, i)
            if sub is None:
                return -1
            i += consumed
            continue
        if text[i] == "`":
            end = _find_backtick(text, i + 1)
            if end == -1:
                return -1
            i = end + 1
            continue
        if text[i] == '"':
            return i
        i += 1
    return -1


def _find_matching_brace(text: str, start: int) -> int:
    depth = 1
    i = start
    in_double = False
    while i < len(text):
        if in_double:
            if text[i] == "\\":
                i += 2
                continue
            if text[i] == '"':
                in_double = False
            i += 1
            continue
        if text[i] == '"':
            in_double = True
            i += 1
            continue
        if text[i] == "'":
            prev = text[i - 1] if i - 1 >= start else ""
            if prev in {"+", "-", ":", "=", "?", "%", "#", "/", "{", "[", " ", "\t", "\n"}:
                sq_end = _scan_single_quote_atom(text, i + 1)
                if sq_end != -1:
                    i = sq_end
                    continue
            i += 1
            continue
        if text[i] == "\\":
            i += 2
            continue
        if text.startswith("${", i):
            depth += 1
            i += 2
            continue
        if (
            text[i] == "}"
            and i - 2 >= start
            and text[i - 1] == "'"
            and i + 1 < len(text)
            and text[i + 1] == "'"
        ):
            opener_prev = text[i - 2]
            if opener_prev in {"+", "-", ":", "=", "?", "%", "#", "/", "{", "[", " ", "\t", "\n"}:
                i += 1
                continue
        if text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
            i += 1
            continue
        i += 1
    return -1


def _scan_single_quote_atom(text: str, start: int) -> int:
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "'":
            return i + 1
        if ch == "\n":
            return -1
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


def _find_ansi_c_single_quote_end(text: str, start: int) -> int:
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            i += 2
            continue
        if ch == "'":
            return i
        i += 1
    return -1


def _decode_backtick_inner(text: str, *, in_double: bool) -> str:
    out: list[str] = []
    i = 0
    specials = {"\\", "`", "$"}
    if in_double:
        specials.add('"')
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "\n":
                i += 2
                continue
            if nxt in specials:
                out.append(nxt)
                i += 2
                continue
            out.append("\\")
            out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _parse_command_sub(text: str, start: int) -> tuple[str | None, int]:
    if not text.startswith("$(", start):
        return None, 1
    i = start + 2
    depth = 1
    case_depth = 0
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text.startswith("<<-", i) or text.startswith("<<", i):
            new_i = _skip_heredoc_in_command_sub(text, i)
            if new_i > i:
                i = new_i
                continue
        if text[i] == "#" and (i == 0 or text[i - 1] in " \t\r\n;("):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if text[i] == "'":
            end = text.find("'", i + 1)
            if end == -1:
                return None, 1
            i = end + 1
            continue
        if text[i] == '"':
            end = _find_matching_quote(text, i + 1)
            if end == -1:
                return None, 1
            i = end + 1
            continue
        if text[i] == "`":
            end = _find_backtick(text, i + 1)
            if end == -1:
                return None, 1
            i = end + 1
            continue
        if text.startswith("$(", i):
            depth += 1
            i += 2
            continue
        if text[i].isalpha() or text[i] == "_":
            j = i + 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            word = text[i:j]
            if word == "case":
                case_depth += 1
            elif word == "esac" and case_depth > 0:
                case_depth -= 1
            i = j
            continue
        if text[i] == "(":
            depth += 1
            i += 1
            continue
        if text[i] == ")":
            if depth == 1 and case_depth > 0:
                i += 1
                continue
            depth -= 1
            i += 1
            if depth == 0:
                inner = text[start + 2 : i - 1]
                return inner, i - start
            continue
        i += 1
    return None, 1


def _looks_like_arith_expr(expr: str) -> bool:
    # Disambiguate `$(( ... ))` vs `$( ( ... ) )` command-substitution forms.
    # A semicolon is valid in shell command lists but not in arithmetic terms.
    if ";" in expr:
        return False
    return True


def _skip_heredoc_in_command_sub(text: str, op_idx: int) -> int:
    strip_tabs = text.startswith("<<-", op_idx)
    op_len = 3 if strip_tabs else 2
    i = op_idx + op_len
    while i < len(text) and text[i] in " \t":
        i += 1
    if i >= len(text) or text[i] == "\n":
        return op_idx
    dstart = i
    while i < len(text) and text[i] not in " \t\r\n":
        i += 1
    dtoken = text[dstart:i]
    delim = _normalize_heredoc_delim(dtoken)
    if not delim:
        return op_idx
    while i < len(text) and text[i] != "\n":
        i += 1
    if i < len(text) and text[i] == "\n":
        i += 1
    while i < len(text):
        j = text.find("\n", i)
        if j == -1:
            line = text[i:]
            next_i = len(text)
        else:
            line = text[i:j]
            next_i = j + 1
        cmp_line = line.lstrip("\t") if strip_tabs else line
        if cmp_line == delim:
            return next_i
        i = next_i
    return len(text)


def _normalize_heredoc_delim(token: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(token):
        ch = token[i]
        if ch in {"'", '"'}:
            i += 1
            continue
        if ch == "\\" and i + 1 < len(token):
            out.append(token[i + 1])
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)




def _parse_arith_sub(text: str, start: int) -> tuple[str | None, int]:
    if not text.startswith("$((", start):
        return None, 1
    i = start + 3
    depth = 1
    paren_depth = 0
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
        if text.startswith("((", i):
            depth += 1
            i += 2
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
            i += 2
            if depth == 0:
                inner = text[start + 3 : i - 2]
                return inner, i - start
            continue
        if ch == ")" and paren_depth > 0:
            paren_depth -= 1
            i += 1
            continue
        i += 1
    return None, 1


def _parse_braced_var(text: str, start: int) -> tuple[LstWordPart | None, int]:
    if not text.startswith("${", start):
        return None, 1
    end = _find_matching_brace(text, start + 2)
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
    transform_ops = {"Q", "P", "A", "a", "E", "U", "u", "L"}
    def _consume_subscript(text: str, j: int) -> int:
        if j >= len(text) or text[j] != "[":
            return j
        k = j + 1
        while k < len(text) and text[k] != "]":
            k += 1
        if k >= len(text):
            return j
        return k + 1

    def _parse_param_name(text: str) -> tuple[str | None, int]:
        if not text:
            return None, 0
        if text[0] in "@*#?$!-":
            return text[0], 1
        if text[0].isdigit():
            j = 1
            while j < len(text) and text[j].isdigit():
                j += 1
            return text[:j], j
        if text[0].isalpha() or text[0] == "_":
            j = 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            j2 = _consume_subscript(text, j)
            if j2 != j:
                j = j2
            return text[:j], j
        return None, 0

    i = 0
    if not inner:
        return None, None, None
    if inner.startswith("#") and len(inner) > 1:
        len_name, used = _parse_param_name(inner[1:])
        if len_name is not None and used == len(inner) - 1:
            return len_name, "__len__", None
    if inner.startswith("!"):
        rest_inner = inner[1:]
        # Keep ${!?} on the normal special-parameter path so it parses as
        # parameter '!' with operator '?' (not bash indirect expansion).
        if len(rest_inner) == 1 and (rest_inner[0] in "@*#$!-" or rest_inner[0].isdigit()):
            return rest_inner, "__indirect__", None
        if rest_inner.isdigit():
            return rest_inner, "__indirect__", None
        if rest_inner and (rest_inner[0].isalpha() or rest_inner[0] == "_"):
            j = 1
            while j < len(rest_inner) and (rest_inner[j].isalnum() or rest_inner[j] == "_"):
                j += 1
            base = rest_inner[:j]
            rest = rest_inner[j:]
            if rest == "[@]":
                return base, "__keys__", "@"
            if rest == "[*]":
                return base, "__keys__", "*"
            if rest == "":
                return base, "__indirect__", None
            return None, None, None
    if inner[0] in "@*#?$!-" and len(inner) >= 1:
        name = inner[0]
        i = 1
        if i >= len(inner):
            return name, None, None
        if inner[i] == "@":
            if i + 1 >= len(inner) or inner[i + 1] not in transform_ops or i + 2 != len(inner):
                return name, "__invalid__", None
            return name, "@" + inner[i + 1], None
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
        return name, "__invalid__", None
    if inner[0].isdigit():
        j = 1
        while j < len(inner) and inner[j].isdigit():
            j += 1
        name = inner[:j]
        i = j
        if i >= len(inner):
            return name, None, None
        if inner[i] == "@":
            if i + 1 >= len(inner) or inner[i + 1] not in transform_ops or i + 2 != len(inner):
                return name, "__invalid__", None
            return name, "@" + inner[i + 1], None
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
        return name, "__invalid__", None
    name_chars: list[str] = []
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
    if inner[i] == "@":
        if i + 1 >= len(inner) or inner[i + 1] not in transform_ops or i + 2 != len(inner):
            return name, "__invalid__", None
        return name, "@" + inner[i + 1], None
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
    return name, "__invalid__", None
