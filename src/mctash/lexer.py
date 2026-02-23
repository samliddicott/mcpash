from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Optional


class LexError(Exception):
    pass


@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int
    index: int


OPERATORS = {
    "&&",
    "||",
    ">>",
    "<>",
    "<<",
    "<<-",
    ">&",
    "<&",
    ";;",
    "(",
    ")",
    ";",
    "|",
    "&",
    "<",
    ">",
    "\n",
}

@dataclass(frozen=True)
class LexContext:
    reserved_words: set[str]
    allow_reserved: bool = True
    allow_newline: bool = True


class TokenReader:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.col = 1
        self._queue: list[Token] = []
        self._pending_heredocs: list[tuple[str, bool, bool]] = []

    def next(self, ctx: LexContext) -> Optional[Token]:
        if self._queue:
            return self._queue.pop(0)
        while self.i < len(self.source):
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "#":
                while self.i < len(self.source) and self._peek() != "\n":
                    self._advance()
                continue
            if ch == "\\" and self._peek(1) == "\n" and self._is_line_continuation():
                self._advance(2)
                continue
            if ch == "\n":
                newline_token = Token("OP", "\n", self.line, self.col, self.i)
                self._advance()
                if self._pending_heredocs:
                    self._capture_heredocs()
                if ctx.allow_newline:
                    return newline_token
                if self._queue:
                    return self._queue.pop(0)
                continue
            if ch in ["&", "|"] and self._peek(1) == "\\" and self._peek(2) == "\n" and self._peek(3) == ch:
                tok = Token("OP", ch + ch, self.line, self.col, self.i)
                self._advance(4)
                return tok
            if ch == ";" and self._peek(1) == "\\" and self._peek(2) == "\n" and self._peek(3) == ";":
                tok = Token("OP", ";;", self.line, self.col, self.i)
                self._advance(4)
                return tok
            if (
                ch == "<"
                and self._peek(1) == "\\"
                and self._peek(2) == "\n"
                and self._peek(3) == "<"
                and self._peek(4) == "\\"
                and self._peek(5) == "\n"
                and self._peek(6) == "-"
            ):
                tok = Token("OP", "<<-", self.line, self.col, self.i)
                self._advance(7)
                self._pending_heredocs.append(("<PENDING>", True, False))
                return tok
            if (
                ch == "<"
                and self._peek(1) == "\\"
                and self._peek(2) == "\n"
                and self._peek(3) == "<"
                and self._peek(4) == "-"
                and self._peek(5) == "\\"
                and self._peek(6) == "\n"
            ):
                tok = Token("OP", "<<-", self.line, self.col, self.i)
                self._advance(7)
                self._pending_heredocs.append(("<PENDING>", True, False))
                return tok
            if ch == "<" and self._peek(1) == "\\" and self._peek(2) == "\n" and self._peek(3) == "<":
                tok = Token("OP", "<<", self.line, self.col, self.i)
                self._advance(4)
                self._pending_heredocs.append(("<PENDING>", False, False))
                return tok
            if (
                ch == "<"
                and self._peek(1) == "<"
                and self._peek(2) == "\\"
                and self._peek(3) == "\n"
                and self._peek(4) == "-"
            ):
                tok = Token("OP", "<<-", self.line, self.col, self.i)
                self._advance(5)
                self._pending_heredocs.append(("<PENDING>", True, False))
                return tok

            three = ch + self._peek(1) + self._peek(2)
            if three in OPERATORS:
                tok = Token("OP", three, self.line, self.col, self.i)
                self._advance(3)
                if three == "<<-":
                    self._pending_heredocs.append(("<PENDING>", True, False))
                return tok
            two = ch + self._peek(1)
            if two in OPERATORS:
                tok = Token("OP", two, self.line, self.col, self.i)
                self._advance(2)
                if two == "<<":
                    self._pending_heredocs.append(("<PENDING>", False, False))
                return tok
            if ch in OPERATORS:
                tok = Token("OP", ch, self.line, self.col, self.i)
                self._advance()
                return tok

            start_line, start_col, start_index = self.line, self.col, self.i
            buf: List[str] = []
            while self.i < len(self.source):
                ch = self._peek()
                if ch in " \t\r\n":
                    break
                two = ch + self._peek(1)
                if two in OPERATORS or ch in OPERATORS:
                    break
                if ch == "'":
                    quote_line, quote_col = self.line, self.col
                    buf.append("'")
                    self._advance()
                    while self.i < len(self.source) and self._peek() != "'":
                        buf.append(self._peek())
                        self._advance()
                    if self._peek() == "'":
                        buf.append("'")
                        self._advance()
                    else:
                        raise LexError(f"syntax error: unterminated quoted string at {quote_line}:{quote_col}")
                    continue
                if ch == '"':
                    quote_line, quote_col = self.line, self.col
                    buf.append('"')
                    self._advance()
                    while self.i < len(self.source) and self._peek() != '"':
                        if self._peek() == "$" and self._peek(1) == "(":
                            chunk, new_i = _scan_command_sub(self.source, self.i)
                            buf.append(chunk)
                            self._advance_to(new_i)
                            continue
                        if self._peek() == "`":
                            chunk, new_i = _scan_backtick_sub(self.source, self.i)
                            buf.append(chunk)
                            self._advance_to(new_i)
                            continue
                        if self._peek() == "\\" and self._peek(1) in ['"', "\\", "$", "`"]:
                            buf.append("\\")
                            self._advance()
                            buf.append(self._peek())
                            self._advance()
                            continue
                        buf.append(self._peek())
                        self._advance()
                    if self._peek() == '"':
                        buf.append('"')
                        self._advance()
                    else:
                        raise LexError(f"syntax error: unterminated quoted string at {quote_line}:{quote_col}")
                    continue
                if ch == "`":
                    quote_line, quote_col = self.line, self.col
                    buf.append("`")
                    self._advance()
                    while self.i < len(self.source) and self._peek() != "`":
                        if self._peek() == "\\" and self._peek(1):
                            buf.append("\\")
                            self._advance()
                            buf.append(self._peek())
                            self._advance()
                            continue
                        buf.append(self._peek())
                        self._advance()
                    if self._peek() == "`":
                        buf.append("`")
                        self._advance()
                    else:
                        raise LexError(f"syntax error: unterminated quoted string at {quote_line}:{quote_col}")
                    continue
                if ch == "$" and self._peek(1) == "(":
                    if self._peek(2) == "(":
                        chunk, new_i = _scan_arith_sub(self.source, self.i)
                    else:
                        chunk, new_i = _scan_command_sub(self.source, self.i)
                    buf.append(chunk)
                    self._advance_to(new_i)
                    continue
                if ch == "\\" and self._peek(1) == "\n":
                    if self._is_line_continuation():
                        self._advance(2)
                        continue
                    buf.append(ch)
                    self._advance()
                    continue
                buf.append(ch)
                self._advance()
            word = "".join(buf)
            if self._pending_heredocs:
                for idx, (delim, strip_tabs, _) in enumerate(self._pending_heredocs):
                    if delim == "<PENDING>":
                        quoted = _is_quoted(word)
                        self._pending_heredocs[idx] = (_strip_quotes(word), strip_tabs, quoted)
                        break
            kind = "WORD"
            if ctx.allow_reserved and word in ctx.reserved_words:
                kind = "RESERVED"
            return Token(kind, word, start_line, start_col, start_index)
        if self._pending_heredocs:
            self._capture_heredocs()
            if self._queue:
                return self._queue.pop(0)
        return None

    def _advance(self, n: int = 1) -> None:
        for _ in range(n):
            if self.i >= len(self.source):
                return
            ch = self.source[self.i]
            self.i += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def _advance_to(self, new_index: int) -> None:
        while self.i < new_index:
            self._advance()

    def _peek(self, n: int = 0) -> str:
        if self.i + n >= len(self.source):
            return ""
        return self.source[self.i + n]

    def _is_line_continuation(self) -> bool:
        if self._peek() != "\\" or self._peek(1) != "\n":
            return False
        n = 0
        j = self.i
        while j >= 0 and self.source[j] == "\\":
            n += 1
            j -= 1
        return (n % 2) == 1

    def _capture_heredocs(self) -> None:
        while self._pending_heredocs:
            delimiter, strip_tabs, quoted = self._pending_heredocs.pop(0)
            if delimiter == "<PENDING>":
                continue
            content, end_index = _consume_heredoc(self.source, self.i, delimiter, strip_tabs, quoted)
            heredoc_value = f"{'Q' if quoted else 'E'}:{'T' if strip_tabs else 'N'}:{content}"
            self._queue.append(Token("HEREDOC", heredoc_value, self.line, self.col, self.i))
            self._advance_to(end_index)


def tokenize(source: str) -> Iterator[Token]:
    ctx = LexContext(reserved_words=set())
    reader = TokenReader(source)
    while True:
        tok = reader.next(ctx)
        if tok is None:
            break
        yield tok


def _consume_heredoc(
    source: str,
    start: int,
    delimiter: str,
    strip_tabs: bool,
    quoted: bool,
) -> tuple[str, int]:
    i = start
    lines: List[str] = []
    logical_line = ""
    logical_had_newline = False
    while i < len(source):
        line_start = i
        while i < len(source) and source[i] != "\n":
            i += 1
        line = source[line_start:i]
        has_newline = i < len(source) and source[i] == "\n"
        if has_newline:
            i += 1

        current = line
        if strip_tabs and logical_line == "":
            current = current.lstrip("\t")

        if not quoted and _has_unescaped_trailing_backslash(current) and has_newline:
            logical_line += current[:-1]
            continue

        logical_line += current
        logical_had_newline = has_newline
        cmp_line = logical_line
        if cmp_line == delimiter:
            break
        lines.append(logical_line)
        if logical_had_newline:
            lines.append("\n")
        logical_line = ""
        logical_had_newline = False
    return "".join(lines), i


def _has_unescaped_trailing_backslash(text: str) -> bool:
    n = 0
    i = len(text) - 1
    while i >= 0 and text[i] == "\\":
        n += 1
        i -= 1
    return (n % 2) == 1


def _strip_quotes(text: str) -> str:
    out: list[str] = []
    i = 0
    in_single = False
    in_double = False
    while i < len(text):
        ch = text[i]
        if in_single:
            if ch == "'":
                in_single = False
            else:
                out.append(ch)
            i += 1
            continue
        if in_double:
            if ch == '"':
                in_double = False
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text):
                nxt = text[i + 1]
                if nxt in ['"', "\\", "$", "`", "\n"]:
                    out.append(nxt)
                else:
                    out.append("\\")
                    out.append(nxt)
                i += 2
                continue
            out.append(ch)
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
            out.append(text[i + 1])
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _is_quoted(text: str) -> bool:
    return any(ch in text for ch in ["\\", "'", '"', "`"])


def _scan_command_sub(source: str, start: int) -> tuple[str, int]:
    i = start
    if not source.startswith("$(", start):
        return source[start:start + 1], start + 1
    i += 2
    depth = 1
    in_single = False
    in_double = False
    while i < len(source):
        ch = source[i]
        if in_single:
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if ch == "\\" and i + 1 < len(source):
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
        if source.startswith("$(", i):
            depth += 1
            i += 2
            continue
        if ch == ")":
            depth -= 1
            i += 1
            if depth == 0:
                return source[start:i], i
            continue
        i += 1
    return source[start:i], i


def _scan_arith_sub(source: str, start: int) -> tuple[str, int]:
    i = start
    if not source.startswith("$((", start):
        return source[start:start + 1], start + 1
    i += 3
    depth = 1
    paren_depth = 0
    in_single = False
    in_double = False
    while i < len(source):
        ch = source[i]
        if in_single:
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if ch == "\\" and i + 1 < len(source):
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
        if source.startswith("$((", i):
            depth += 1
            i += 3
            continue
        if source.startswith("))", i) and (depth > 1 or paren_depth == 0):
            depth -= 1
            i += 2
            if depth == 0:
                return source[start:i], i
            continue
        if ch == "(":
            paren_depth += 1
            i += 1
            continue
        if ch == ")":
            if paren_depth > 0:
                paren_depth -= 1
                i += 1
                continue
        i += 1
    return source[start:i], i


def _scan_backtick_sub(source: str, start: int) -> tuple[str, int]:
    i = start
    if not source.startswith("`", start):
        return source[start:start + 1], start + 1
    i += 1
    while i < len(source):
        ch = source[i]
        if ch == "\\" and i + 1 < len(source):
            i += 2
            continue
        if ch == "`":
            i += 1
            return source[start:i], i
        i += 1
    return source[start:i], i
