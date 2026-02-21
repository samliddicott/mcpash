from __future__ import annotations

from typing import List, Optional

from .ast_nodes import AndOr, Assignment, Command, ListNode, Pipeline, Redirect, Script, Word
from .lexer import Token


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _advance(self) -> Optional[Token]:
        tok = self._peek()
        if tok is not None:
            self.pos += 1
        return tok

    def _expect_op(self, op: str) -> Token:
        tok = self._peek()
        if tok is None or tok.kind != "OP" or tok.value != op:
            raise ParseError(f"expected {op!r} at {self._where(tok)}")
        self._advance()
        return tok

    def _where(self, tok: Optional[Token]) -> str:
        if tok is None:
            return "eof"
        return f"{tok.line}:{tok.col}"

    def parse_script(self) -> Script:
        body = self.parse_list()
        return Script(body=body)

    def parse_next(self) -> Optional[AndOr]:
        while True:
            tok = self._peek()
            if tok is None:
                return None
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
                self._advance()
                continue
            break
        node = self.parse_and_or()
        tok = self._peek()
        if tok and tok.kind == "OP" and tok.value in ["\n", ";"]:
            self._advance()
        return node

    def parse_list(self) -> ListNode:
        items: List[AndOr] = []
        while True:
            if self._peek() is None:
                break
            if self._peek().kind == "OP" and self._peek().value == "\n":
                self._advance()
                continue
            items.append(self.parse_and_or())
            tok = self._peek()
            if tok is None:
                break
            if tok.kind == "OP" and tok.value in [";", "\n"]:
                self._advance()
                continue
        return ListNode(items=items)

    def parse_and_or(self) -> AndOr:
        pipelines: List[Pipeline] = [self.parse_pipeline()]
        operators: List[str] = []
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value in ["&&", "||"]:
                operators.append(tok.value)
                self._advance()
                pipelines.append(self.parse_pipeline())
                continue
            break
        return AndOr(pipelines=pipelines, operators=operators)

    def parse_pipeline(self) -> Pipeline:
        commands: List[Command] = [self.parse_command()]
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "|":
                self._advance()
                commands.append(self.parse_command())
                continue
            break
        return Pipeline(commands=commands, negate=False)

    def parse_command(self) -> Command:
        argv: List[Word] = []
        assignments: List[Assignment] = []
        redirects: List[Redirect] = []
        while True:
            tok = self._peek()
            if tok is None:
                break
            # IO number before redirection
            if tok.kind == "WORD" and tok.value.isdigit():
                next_tok = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if next_tok and next_tok.kind == "OP" and next_tok.value in ["<", ">", ">>", "<<"]:
                    fd = int(tok.value)
                    self._advance()
                    op_tok = self._advance()
                    target_tok = self._peek()
                    if target_tok is None or target_tok.kind != "WORD":
                        raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                    redir = Redirect(op=op_tok.value, target=target_tok.value, fd=fd)
                    self._advance()
                    if redir.op == "<<":
                        here_tok = self._peek()
                        if here_tok and here_tok.kind == "HEREDOC":
                            redir.here_doc = here_tok.value
                            self._advance()
                    redirects.append(redir)
                    continue
            if tok.kind == "OP" and tok.value in ["<", ">", ">>", "<<"]:
                op = tok.value
                self._advance()
                target_tok = self._peek()
                if target_tok is None or target_tok.kind != "WORD":
                    raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                redir = Redirect(op=op, target=target_tok.value)
                self._advance()
                if redir.op == "<<":
                    here_tok = self._peek()
                    if here_tok and here_tok.kind == "HEREDOC":
                        redir.here_doc = here_tok.value
                        self._advance()
                redirects.append(redir)
                continue
            if tok.kind == "WORD":
                if self._is_assignment(tok.value) and not argv:
                    name, value = tok.value.split("=", 1)
                    assignments.append(Assignment(name=name, value=value))
                else:
                    argv.append(Word(tok.value))
                self._advance()
                continue
            break
        if not argv and not assignments and not redirects:
            raise ParseError(f"expected command at {self._where(tok)}")
        return Command(argv=argv, assignments=assignments, redirects=redirects)

    def _is_assignment(self, text: str) -> bool:
        if "=" not in text:
            return False
        name, _ = text.split("=", 1)
        if not name:
            return False
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        return all(ch.isalnum() or ch == "_" for ch in name)


def parse(tokens: List[Token]) -> Script:
    return Parser(tokens).parse_script()
