from __future__ import annotations

from typing import List, Optional

from .ast_nodes import (
    AndOr,
    Assignment,
    Command,
    CaseCommand,
    CaseItem,
    ForCommand,
    FunctionDef,
    GroupCommand,
    IfCommand,
    ListNode,
    Pipeline,
    Redirect,
    Script,
    SimpleCommand,
    SubshellCommand,
    WhileCommand,
    Word,
)
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

    def parse_compound_list(self, stop_words: set[str]) -> ListNode:
        items: List[AndOr] = []
        while True:
            tok = self._peek()
            if tok is None:
                break
            if tok.kind == "WORD" and tok.value in stop_words:
                break
            if tok.kind == "OP" and tok.value in stop_words:
                break
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
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
        tok = self._peek()
        if tok and tok.kind == "WORD" and tok.value == "if":
            return self.parse_if()
        if tok and tok.kind == "WORD" and tok.value in ["while", "until"]:
            return self.parse_while()
        if tok and tok.kind == "WORD" and tok.value == "for":
            return self.parse_for()
        if tok and tok.kind == "WORD" and tok.value == "case":
            return self.parse_case()
        if tok and tok.kind == "OP" and tok.value == "{":
            return self.parse_group()
        if tok and tok.kind == "OP" and tok.value == "(":
            return self.parse_subshell()
        if self._looks_like_function_def():
            return self.parse_function_def()
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
                if next_tok and next_tok.kind == "OP" and next_tok.value in ["<", ">", ">>", "<<", "<<-", ">&", "<&"]:
                    fd = int(tok.value)
                    self._advance()
                    op_tok = self._advance()
                    target_tok = self._peek()
                    if target_tok is None or target_tok.kind != "WORD":
                        raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                    redir = self._make_redirect(op_tok.value, target_tok.value, fd)
                    self._advance()
                    if redir.op == "<<":
                        here_tok = self._peek()
                        if here_tok and here_tok.kind == "HEREDOC":
                            self._apply_heredoc_token(redir, here_tok.value)
                            self._advance()
                    if redir.op == "<<-":
                        here_tok = self._peek()
                        if here_tok and here_tok.kind == "HEREDOC":
                            self._apply_heredoc_token(redir, here_tok.value)
                            self._advance()
                    redirects.append(redir)
                    continue
            if tok.kind == "OP" and tok.value in ["<", ">", ">>", "<<", "<<-", ">&", "<&"]:
                op = tok.value
                self._advance()
                target_tok = self._peek()
                if target_tok is None or target_tok.kind != "WORD":
                    raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                redir = self._make_redirect(op, target_tok.value, None)
                self._advance()
                if redir.op in ["<<", "<<-"]:
                    here_tok = self._peek()
                    if here_tok and here_tok.kind == "HEREDOC":
                        self._apply_heredoc_token(redir, here_tok.value)
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
        return SimpleCommand(argv=argv, assignments=assignments, redirects=redirects)

    def _is_assignment(self, text: str) -> bool:
        if "=" not in text:
            return False
        name, _ = text.split("=", 1)
        if not name:
            return False
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        return all(ch.isalnum() or ch == "_" for ch in name)

    def _make_redirect(self, op: str, target: str, fd: int | None) -> Redirect:
        if op == "<<-":
            return Redirect(op="<<", target=target, fd=fd, here_doc_strip_tabs=True)
        return Redirect(op=op, target=target, fd=fd)

    def _apply_heredoc_token(self, redir: Redirect, token_value: str) -> None:
        parts = token_value.split(":", 2)
        if len(parts) == 3:
            expand_flag, strip_flag, content = parts
            redir.here_doc_expand = expand_flag == "E"
            redir.here_doc_strip_tabs = strip_flag == "T"
            redir.here_doc = content
        else:
            redir.here_doc = token_value

    def parse_group(self) -> GroupCommand:
        self._expect_op("{")
        body = self.parse_compound_list({"}"})
        self._expect_op("}")
        return GroupCommand(body=body)

    def parse_function_def(self) -> FunctionDef:
        name_tok = self._advance()
        if name_tok is None or name_tok.kind != "WORD":
            raise ParseError(f"expected function name at {self._where(name_tok)}")
        self._expect_op("(")
        self._expect_op(")")
        body_cmd = self.parse_group()
        return FunctionDef(name=name_tok.value, body=body_cmd.body)

    def parse_subshell(self) -> SubshellCommand:
        self._expect_op("(")
        body = self.parse_compound_list({")"})
        self._expect_op(")")
        return SubshellCommand(body=body)

    def parse_for(self) -> ForCommand:
        tok = self._advance()
        if tok is None or tok.kind != "WORD" or tok.value != "for":
            raise ParseError(f"expected for at {self._where(tok)}")
        name_tok = self._advance()
        if name_tok is None or name_tok.kind != "WORD":
            raise ParseError(f"expected name at {self._where(name_tok)}")
        items: List[Word] = []
        tok = self._peek()
        if tok and tok.kind == "WORD" and tok.value == "in":
            self._advance()
            while True:
                tok = self._peek()
                if tok is None:
                    break
                if tok.kind == "WORD" and tok.value == "do":
                    break
                if tok.kind == "OP" and tok.value in [";", "\n"]:
                    self._advance()
                    continue
                if tok.kind == "WORD":
                    items.append(Word(tok.value))
                    self._advance()
                    continue
                break
        do_tok = self._advance()
        if do_tok is None or do_tok.kind != "WORD" or do_tok.value != "do":
            raise ParseError(f"expected do at {self._where(do_tok)}")
        body = self.parse_compound_list({"done"})
        done_tok = self._advance()
        if done_tok is None or done_tok.kind != "WORD" or done_tok.value != "done":
            raise ParseError(f"expected done at {self._where(done_tok)}")
        return ForCommand(name=name_tok.value, items=items, body=body)

    def parse_case(self) -> CaseCommand:
        tok = self._advance()
        if tok is None or tok.kind != "WORD" or tok.value != "case":
            raise ParseError(f"expected case at {self._where(tok)}")
        word_tok = self._advance()
        if word_tok is None or word_tok.kind != "WORD":
            raise ParseError(f"expected case word at {self._where(word_tok)}")
        in_tok = self._advance()
        if in_tok is None or in_tok.kind != "WORD" or in_tok.value != "in":
            raise ParseError(f"expected in at {self._where(in_tok)}")
        items: List[CaseItem] = []
        while True:
            tok = self._peek()
            if tok is None:
                break
            if tok.kind == "WORD" and tok.value == "esac":
                self._advance()
                break
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
                self._advance()
                continue
            patterns: List[str] = []
            while True:
                tok = self._peek()
                if tok is None:
                    break
                if tok.kind == "OP" and tok.value == ")":
                    self._advance()
                    break
                if tok.kind == "WORD":
                    part = tok.value
                    self._advance()
                    if part.endswith("|"):
                        part = part[:-1]
                        patterns.append(part)
                        continue
                    patterns.append(part)
                    tok2 = self._peek()
                    if tok2 and tok2.kind == "OP" and tok2.value == "|":
                        self._advance()
                        continue
                    continue
                if tok.kind == "OP" and tok.value == "|":
                    self._advance()
                    continue
                break
            body = self.parse_compound_list({";;", "esac"})
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == ";;":
                self._advance()
            items.append(CaseItem(patterns=patterns, body=body))
        return CaseCommand(value=Word(word_tok.value), items=items)

    def parse_if(self) -> IfCommand:
        tok = self._advance()
        if tok is None or tok.value != "if":
            raise ParseError(f"expected if at {self._where(tok)}")
        cond = self.parse_compound_list({"then"})
        then_tok = self._advance()
        if then_tok is None or then_tok.kind != "WORD" or then_tok.value != "then":
            raise ParseError(f"expected then at {self._where(then_tok)}")
        then_body = self.parse_compound_list({"else", "elif", "fi"})
        elifs: List[tuple[ListNode, ListNode]] = []
        else_body = None
        while True:
            tok = self._peek()
            if tok and tok.kind == "WORD" and tok.value == "elif":
                self._advance()
                elif_cond = self.parse_compound_list({"then"})
                then_tok = self._advance()
                if then_tok is None or then_tok.kind != "WORD" or then_tok.value != "then":
                    raise ParseError(f"expected then at {self._where(then_tok)}")
                elif_body = self.parse_compound_list({"else", "elif", "fi"})
                elifs.append((elif_cond, elif_body))
                continue
            break
        tok = self._peek()
        if tok and tok.kind == "WORD" and tok.value == "else":
            self._advance()
            else_body = self.parse_compound_list({"fi"})
        end_tok = self._advance()
        if end_tok is None or end_tok.kind != "WORD" or end_tok.value != "fi":
            raise ParseError(f"expected fi at {self._where(end_tok)}")
        return IfCommand(cond=cond, then_body=then_body, elifs=elifs, else_body=else_body)

    def parse_while(self) -> WhileCommand:
        tok = self._advance()
        if tok is None or tok.kind != "WORD" or tok.value not in ["while", "until"]:
            raise ParseError(f"expected while/until at {self._where(tok)}")
        until = tok.value == "until"
        cond = self.parse_compound_list({"do"})
        do_tok = self._advance()
        if do_tok is None or do_tok.kind != "WORD" or do_tok.value != "do":
            raise ParseError(f"expected do at {self._where(do_tok)}")
        body = self.parse_compound_list({"done"})
        done_tok = self._advance()
        if done_tok is None or done_tok.kind != "WORD" or done_tok.value != "done":
            raise ParseError(f"expected done at {self._where(done_tok)}")
        return WhileCommand(cond=cond, body=body, until=until)

    def _looks_like_function_def(self) -> bool:
        tok = self._peek()
        if tok is None or tok.kind != "WORD":
            return False
        if self.pos + 2 >= len(self.tokens):
            return False
        tok1 = self.tokens[self.pos + 1]
        tok2 = self.tokens[self.pos + 2]
        if tok1.kind == "OP" and tok1.value == "(" and tok2.kind == "OP" and tok2.value == ")":
            return True
        return False


def parse(tokens: List[Token]) -> Script:
    return Parser(tokens).parse_script()
