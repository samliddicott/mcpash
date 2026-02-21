from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List


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


def tokenize(source: str) -> Iterator[Token]:
    i = 0
    line = 1
    col = 1
    pending_heredoc: str | None = None

    def advance(n: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(n):
            if i >= len(source):
                return
            ch = source[i]
            i += 1
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1

    def peek(n: int = 0) -> str:
        if i + n >= len(source):
            return ""
        return source[i + n]

    while i < len(source):
        ch = peek()
        if ch in " \t\r":
            advance()
            continue
        if ch == "\\" and peek(1) == "\n":
            advance(2)
            continue
        if ch == "\n":
            yield Token("OP", "\n", line, col, i)
            advance()
            if pending_heredoc is not None:
                content, end_index = _consume_heredoc(source, i, pending_heredoc)
                yield Token("HEREDOC", content, line, col, i)
                pending_heredoc = None
                while i < end_index:
                    advance()
            continue

        # Operators (2-char then 1-char)
        two = ch + peek(1)
        if two in OPERATORS:
            yield Token("OP", two, line, col, i)
            advance(2)
            if two == "<<":
                pending_heredoc = "<PENDING>"
            continue
        if ch in OPERATORS:
            yield Token("OP", ch, line, col, i)
            advance()
            continue

        # Word scanning with minimal quote handling
        start_line, start_col, start_index = line, col, i
        buf: List[str] = []
        while i < len(source):
            ch = peek()
            if ch in " \t\r\n":
                break
            two = ch + peek(1)
            if two in OPERATORS or ch in OPERATORS:
                break
            if ch == "'":
                buf.append("'")
                advance()
                while i < len(source) and peek() != "'":
                    buf.append(peek())
                    advance()
                if peek() == "'":
                    buf.append("'")
                    advance()
                continue
            if ch == '"':
                buf.append('"')
                advance()
                while i < len(source) and peek() != '"':
                    if peek() == "\\" and peek(1) in ['"', "\\", "$", "`"]:
                        buf.append("\\")
                        advance()
                        buf.append(peek())
                        advance()
                        continue
                    buf.append(peek())
                    advance()
                if peek() == '"':
                    buf.append('"')
                    advance()
                continue
            buf.append(ch)
            advance()
        word = "".join(buf)
        yield Token("WORD", word, start_line, start_col, start_index)
        if pending_heredoc == "<PENDING>":
            pending_heredoc = _strip_quotes(word)


def _consume_heredoc(source: str, start: int, delimiter: str) -> tuple[str, int]:
    i = start
    lines: List[str] = []
    while i < len(source):
        line_start = i
        while i < len(source) and source[i] != "\n":
            i += 1
        line = source[line_start:i]
        if line == delimiter:
            if i < len(source) and source[i] == "\n":
                i += 1
            break
        lines.append(line)
        if i < len(source) and source[i] == "\n":
            lines.append("\n")
            i += 1
    return "".join(lines), i


def _strip_quotes(text: str) -> str:
    if len(text) >= 2 and ((text[0] == text[-1] == "'") or (text[0] == text[-1] == '"')):
        return text[1:-1]
    return text
