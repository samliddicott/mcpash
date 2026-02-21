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


def tokenize(source: str) -> Iterator[Token]:
    i = 0
    line = 1
    col = 1
    pending_heredoc: tuple[str, bool, bool] | None = None  # (delimiter, strip_tabs, quoted)

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
        if ch == "#":
            while i < len(source) and peek() != "\n":
                advance()
            continue
        if ch == "\\" and peek(1) == "\n":
            advance(2)
            continue
        if ch == "\n":
            yield Token("OP", "\n", line, col, i)
            advance()
            if pending_heredoc is not None:
                delimiter, strip_tabs, quoted = pending_heredoc
                content, end_index = _consume_heredoc(source, i, delimiter, strip_tabs)
                heredoc_value = f"{'Q' if quoted else 'E'}:{'T' if strip_tabs else 'N'}:{content}"
                yield Token("HEREDOC", heredoc_value, line, col, i)
                pending_heredoc = None
                while i < end_index:
                    advance()
            continue

        # Operators (3-char then 2-char then 1-char)
        three = ch + peek(1) + peek(2)
        if three in OPERATORS:
            yield Token("OP", three, line, col, i)
            advance(3)
            if three == "<<-":
                pending_heredoc = ("<PENDING>", True, False)
            continue
        two = ch + peek(1)
        if two in OPERATORS:
            yield Token("OP", two, line, col, i)
            advance(2)
            if two == "<<":
                pending_heredoc = ("<PENDING>", False, False)
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
        if pending_heredoc is not None and pending_heredoc[0] == "<PENDING>":
            _, strip_tabs, _ = pending_heredoc
            quoted = _is_quoted(word)
            pending_heredoc = (_strip_quotes(word), strip_tabs, quoted)


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
