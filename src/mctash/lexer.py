from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Optional


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
    "<<",
    "<<-",
    ">&",
    "<&",
    ";;",
    ";",
    "|",
    "&",
    "(",
    ")",
    "{",
    "}",
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
            if ch == "\\" and self._peek(1) == "\n":
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
                    buf.append("'")
                    self._advance()
                    while self.i < len(self.source) and self._peek() != "'":
                        buf.append(self._peek())
                        self._advance()
                    if self._peek() == "'":
                        buf.append("'")
                        self._advance()
                    continue
                if ch == '"':
                    buf.append('"')
                    self._advance()
                    while self.i < len(self.source) and self._peek() != '"':
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
                    continue
                if ch == "$" and self._peek(1) == "(":
                    buf.append("$(")
                    self._advance(2)
                    depth = 1
                    while self.i < len(self.source) and depth > 0:
                        if self._peek() == "(":
                            depth += 1
                            buf.append(self._peek())
                            self._advance()
                            continue
                        if self._peek() == ")":
                            depth -= 1
                            buf.append(")")
                            self._advance()
                            if depth == 0:
                                break
                            continue
                        buf.append(self._peek())
                        self._advance()
                    continue
                buf.append(ch)
                self._advance()
            word = "".join(buf)
            if self._pending_heredocs and self._pending_heredocs[-1][0] == "<PENDING>":
                _, strip_tabs, _ = self._pending_heredocs[-1]
                quoted = _is_quoted(word)
                self._pending_heredocs[-1] = (_strip_quotes(word), strip_tabs, quoted)
            kind = "WORD"
            if ctx.allow_reserved and word in ctx.reserved_words:
                kind = "RESERVED"
            return Token(kind, word, start_line, start_col, start_index)
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

    def _capture_heredocs(self) -> None:
        while self._pending_heredocs:
            delimiter, strip_tabs, quoted = self._pending_heredocs.pop(0)
            if delimiter == "<PENDING>":
                continue
            content, end_index = _consume_heredoc(self.source, self.i, delimiter, strip_tabs)
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


def _consume_heredoc(source: str, start: int, delimiter: str, strip_tabs: bool) -> tuple[str, int]:
    i = start
    lines: List[str] = []
    while i < len(source):
        line_start = i
        while i < len(source) and source[i] != "\n":
            i += 1
        line = source[line_start:i]
        cmp_line = line.lstrip("\t") if strip_tabs else line
        if cmp_line == delimiter:
            if i < len(source) and source[i] == "\n":
                i += 1
            break
        lines.append(line.lstrip("\t") if strip_tabs else line)
        if i < len(source) and source[i] == "\n":
            lines.append("\n")
            i += 1
    return "".join(lines), i


def _strip_quotes(text: str) -> str:
    if len(text) >= 2 and ((text[0] == text[-1] == "'") or (text[0] == text[-1] == '"')):
        return text[1:-1]
    return text


def _is_quoted(text: str) -> bool:
    return len(text) >= 2 and ((text[0] == text[-1] == "'") or (text[0] == text[-1] == '"'))
