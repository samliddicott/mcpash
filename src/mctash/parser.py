from __future__ import annotations
from typing import List, Optional

from .ast_nodes import (
    AndOr,
    Assignment,
    ArithForCommand,
    CaseCommand,
    CaseItem,
    CoprocCommand,
    Command,
    ForCommand,
    FunctionDef,
    GroupCommand,
    IfCommand,
    ListNode,
    ListItem,
    Pipeline,
    Redirect,
    RedirectCommand,
    Script,
    SelectCommand,
    SimpleCommand,
    SubshellCommand,
    WhileCommand,
    Word,
)
from .lexer import LexContext, LexError, Token, TokenReader
from .lst_nodes import (
    LstAndOr,
    LstArithForCommand,
    LstArithSubPart,
    LstAssignment,
    LstCaseCommand,
    LstCaseItem,
    LstCommandSubPart,
    LstCommand,
    LstDoubleQuotedPart,
    LstDoGroup,
    LstForCommand,
    LstFunctionDef,
    LstGroupCommand,
    LstIfCommand,
    LstListItem,
    LstListNode,
    LstLiteralPart,
    LstPipeline,
    LstRedirect,
    LstRedirectCommand,
    LstScript,
    LstShAssignmentCommand,
    LstSimpleCommand,
    LstSelectCommand,
    LstCoprocCommand,
    LstSubshellCommand,
    LstWhileCommand,
    LstWord,
    LstWordPart,
    LstTokenPos,
)
from .word_parser import parse_word


class ParseError(Exception):
    pass


RESERVED_WORDS = {
    "if",
    "then",
    "else",
    "elif",
    "fi",
    "for",
    "in",
    "do",
    "done",
    "case",
    "esac",
    "while",
    "until",
    "select",
    "coproc",
    "function",
}


class Parser:
    def __init__(self, source: str, aliases: Optional[dict[str, str]] = None):
        self.reader = TokenReader(source)
        self.buffer: list[Token] = []
        self.ctx = LexContext(reserved_words=RESERVED_WORDS, allow_reserved=True, allow_newline=True)
        self.last_lst: Optional[LstAndOr] = None
        self.last_lst_item: Optional[LstListItem] = None
        self.last_line: int | None = None
        self.pending_heredocs: List[tuple[Redirect, LstRedirect]] = []
        self.aliases: dict[str, str] = aliases if aliases is not None else {}
        self._saw_command: bool = False
        self._last_token: Optional[Token] = None
        self.last_source_start: int | None = None
        self.last_source_end: int | None = None

    def _peek(self) -> Optional[Token]:
        if not self.buffer:
            try:
                tok = self.reader.next(self.ctx)
            except LexError as e:
                raise ParseError(str(e))
            if tok is not None:
                self.buffer.append(tok)
        return self.buffer[0] if self.buffer else None

    def _peek_n(self, n: int) -> Optional[Token]:
        while len(self.buffer) <= n:
            try:
                tok = self.reader.next(self.ctx)
            except LexError as e:
                raise ParseError(str(e))
            if tok is None:
                break
            self.buffer.append(tok)
        if n < len(self.buffer):
            return self.buffer[n]
        return None

    def _advance(self) -> Optional[Token]:
        tok = self._peek()
        if tok is not None:
            self.buffer.pop(0)
            self._last_token = tok
        return tok

    def _expect_op(self, op: str) -> Token:
        tok = self._peek()
        if tok is None or tok.kind != "OP" or tok.value != op:
            raise ParseError(f"expected {op!r} at {self._where(tok)}")
        self._advance()
        return tok

    def _expect_group_token(self, value: str) -> Token:
        tok = self._peek()
        if tok is None:
            raise ParseError(f"expected {value!r} at {self._where(tok)}")
        if tok.kind == "OP" and tok.value == value:
            self._advance()
            return tok
        if self._is_word(tok) and tok.value == value:
            self._advance()
            return tok
        raise ParseError(f"expected {value!r} at {self._where(tok)}")

    def _where(self, tok: Optional[Token]) -> str:
        if tok is None:
            return f"{self.reader.line}:{self.reader.col}"
        return f"{tok.line}:{tok.col}"

    def _token_adjacent(self, left: Token, right: Token) -> bool:
        return left.index + len(left.value) == right.index

    def _inject_alias_tokens(self, src_tok: Token, text: str) -> bool:
        trailing = bool(text) and text[-1].isspace()
        alias_reader = TokenReader(text)
        alias_ctx = LexContext(reserved_words=RESERVED_WORDS, allow_reserved=True, allow_newline=False)
        alias_tokens: list[Token] = []
        while True:
            tok = alias_reader.next(alias_ctx)
            if tok is None:
                break
            if tok.kind == "OP" and tok.value == "\n":
                continue
            alias_tokens.append(Token(tok.kind, tok.value, src_tok.line, src_tok.col, src_tok.index))
        if alias_tokens:
            self.buffer = alias_tokens + self.buffer
        return trailing

    def _alias_affects_syntax(self, text: str) -> bool:
        if ";" in text or "\n" in text:
            return True
        alias_reader = TokenReader(text)
        alias_ctx = LexContext(reserved_words=RESERVED_WORDS, allow_reserved=True, allow_newline=False)
        tok = alias_reader.next(alias_ctx)
        if tok is None:
            return False
        if tok.kind == "RESERVED":
            return True
        if tok.kind == "WORD" and tok.value in {"{", "}", "(", ")"}:
            return True
        return False

    def _maybe_expand_alias(self, tok: Optional[Token], seen: set[str], syntax_only: bool = False) -> bool:
        if tok is None or not self._is_word(tok):
            return False
        if tok.value not in self.aliases:
            return False
        name = tok.value
        if name not in self.aliases or name in seen:
            return False
        if syntax_only and not self._alias_affects_syntax(self.aliases[name]):
            return False
        seen.add(name)
        self._advance()
        self._inject_alias_tokens(tok, self.aliases[name])
        return True

    def _is_heredoc_only_andor(self, node: AndOr) -> bool:
        if len(node.pipelines) != 1 or node.operators:
            return False
        pl = node.pipelines[0]
        if pl.negate or len(pl.commands) != 1:
            return False
        cmd = pl.commands[0]
        if isinstance(cmd, SimpleCommand):
            return (not cmd.argv) and (not cmd.assignments) and any(r.op == "<<" for r in cmd.redirects)
        return False

    def _is_word(self, tok: Optional[Token]) -> bool:
        return tok is not None and tok.kind in ["WORD", "RESERVED"]

    def parse_script(self) -> Script:
        body, lst_body = self.parse_list()
        lst_script = LstScript(body=lst_body)
        return Script(body=body, lst=lst_script)

    def parse_next(self) -> Optional[ListItem]:
        while True:
            tok = self._peek()
            if tok is None:
                return None
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
                if tok.value == ";" and not self._saw_command:
                    raise ParseError(f"syntax error: unexpected ';' at {self._where(tok)}")
                self._advance()
                continue
            break
        start_tok = tok
        self.last_line = tok.line if tok is not None else None
        node, lst_node = self.parse_and_or()
        self.last_lst = lst_node
        tok = self._peek()
        background = False
        terminator: str | None = None
        consumed_trailing_newline = False
        if tok and tok.kind == "OP" and tok.value in ["\n", ";", "&"]:
            background = tok.value == "&"
            terminator = tok.value
            self._advance()
            if tok.value == "\n":
                self._consume_pending_heredocs()
                consumed_trailing_newline = True
            elif tok.value == ";" and self.pending_heredocs:
                ntok = self._peek()
                if ntok and ntok.kind == "OP" and ntok.value == "\n":
                    self._advance()
                    self._consume_pending_heredocs()
                    consumed_trailing_newline = True
            if tok.value == ";" and self._is_heredoc_only_andor(node):
                ntok = self._peek()
                if self._is_word(ntok) and ntok.value == "then":
                    raise ParseError(f'syntax error: unexpected "then" at {self._where(ntok)}')
        if terminator == ";" and self.pending_heredocs and not consumed_trailing_newline:
            group_items: List[ListItem] = [ListItem(node=node, background=background)]
            lst_group_items: List[LstListItem] = [LstListItem(node=lst_node, terminator=terminator)]
            while True:
                ntok = self._peek()
                if ntok is None:
                    break
                if ntok.kind == "OP" and ntok.value == "\n":
                    self._advance()
                    self._consume_pending_heredocs()
                    break
                next_node, next_lst = self.parse_and_or()
                next_bg = False
                next_term: str | None = None
                ntok = self._peek()
                if ntok and ntok.kind == "OP" and ntok.value in ["\n", ";", "&"]:
                    next_bg = ntok.value == "&"
                    next_term = ntok.value
                    self._advance()
                    if ntok.value == "\n":
                        self._consume_pending_heredocs()
                    elif ntok.value == ";" and self.pending_heredocs:
                        maybe_nl = self._peek()
                        if maybe_nl and maybe_nl.kind == "OP" and maybe_nl.value == "\n":
                            self._advance()
                            self._consume_pending_heredocs()
                group_items.append(ListItem(node=next_node, background=next_bg))
                lst_group_items.append(LstListItem(node=next_lst, terminator=next_term))
                if next_term != ";":
                    break
            group_cmd = GroupCommand(body=ListNode(items=group_items))
            lst_group_cmd = LstGroupCommand(body=LstListNode(items=lst_group_items))
            wrapped = AndOr(pipelines=[Pipeline(commands=[group_cmd], negate=False)], operators=[])
            wrapped_lst = LstAndOr(
                pipelines=[LstPipeline(commands=[lst_group_cmd], negate=False)],
                operators=[],
                op_positions=[],
            )
            self.last_lst = wrapped_lst
            self.last_lst_item = LstListItem(node=wrapped_lst, terminator=None)
            self._saw_command = True
            self.last_source_start = start_tok.index if start_tok is not None else None
            self.last_source_end = self.reader.i
            return ListItem(node=wrapped, background=False)
        self.last_lst_item = LstListItem(node=lst_node, terminator=terminator)
        self._saw_command = True
        self.last_source_start = start_tok.index if start_tok is not None else None
        self.last_source_end = self.reader.i
        return ListItem(node=node, background=background)

    def last_source_text(self) -> str | None:
        if self.last_source_start is None or self.last_source_end is None:
            return None
        if self.last_source_start < 0 or self.last_source_end < self.last_source_start:
            return None
        return self.reader.source[self.last_source_start : self.last_source_end]

    def parse_list(self) -> tuple[ListNode, LstListNode]:
        items: List[ListItem] = []
        lst_items: List[LstListItem] = []
        while True:
            if self._peek() is None:
                break
            if self._peek().kind == "OP" and self._peek().value == "\n":
                self._advance()
                continue
            item, lst_item = self.parse_and_or()
            terminator = None
            tok = self._peek()
            if tok is None:
                items.append(ListItem(node=item))
                lst_items.append(LstListItem(node=lst_item))
                break
            if tok.kind == "OP" and tok.value in [";", "\n", "&"]:
                terminator = tok.value
                self._advance()
                if terminator == "\n":
                    self._consume_pending_heredocs()
                elif terminator == ";" and self.pending_heredocs:
                    ntok = self._peek()
                    if ntok and ntok.kind == "OP" and ntok.value == "\n":
                        self._advance()
                        self._consume_pending_heredocs()
                if terminator == ";" and self._is_heredoc_only_andor(item):
                    ntok = self._peek()
                    if self._is_word(ntok) and ntok.value == "then":
                        raise ParseError(f'syntax error: unexpected "then" at {self._where(ntok)}')
            items.append(ListItem(node=item, background=(terminator == "&")))
            lst_items.append(LstListItem(node=lst_item, terminator=terminator))
            if terminator is None:
                break
        return ListNode(items=items), LstListNode(items=lst_items)

    def parse_compound_list(self, stop_words: set[str]) -> tuple[ListNode, LstListNode]:
        items: List[ListItem] = []
        lst_items: List[LstListItem] = []
        while True:
            tok = self._peek()
            if tok is None:
                break
            if self._is_word(tok) and tok.value in self.aliases:
                seen: set[str] = set()
                if self._maybe_expand_alias(tok, seen, syntax_only=False):
                    tok = self._peek()
                    if tok is None:
                        break
            if self._is_word(tok) and tok.value in stop_words:
                break
            if tok.kind == "OP" and tok.value in stop_words:
                break
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
                self._advance()
                continue
            item, lst_item = self.parse_and_or()
            terminator = None
            tok = self._peek()
            if tok is None:
                items.append(ListItem(node=item))
                lst_items.append(LstListItem(node=lst_item))
                break
            if tok.kind == "OP" and tok.value in [";", "\n", "&"]:
                terminator = tok.value
                self._advance()
                if terminator == "\n":
                    self._consume_pending_heredocs()
                elif terminator == ";" and self.pending_heredocs:
                    ntok = self._peek()
                    if ntok and ntok.kind == "OP" and ntok.value == "\n":
                        self._advance()
                        self._consume_pending_heredocs()
                if terminator == ";" and self._is_heredoc_only_andor(item):
                    ntok = self._peek()
                    if self._is_word(ntok) and ntok.value == "then":
                        raise ParseError(f'syntax error: unexpected "then" at {self._where(ntok)}')
            items.append(ListItem(node=item, background=(terminator == "&")))
            lst_items.append(LstListItem(node=lst_item, terminator=terminator))
            if terminator is None:
                break
        return ListNode(items=items), LstListNode(items=lst_items)

    def parse_and_or(self) -> tuple[AndOr, LstAndOr]:
        pipeline, lst_pipeline = self.parse_pipeline()
        pipelines: List[Pipeline] = [pipeline]
        lst_pipelines: List[LstPipeline] = [lst_pipeline]
        operators: List[str] = []
        op_positions: List[LstTokenPos] = []
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value in ["&&", "||"]:
                operators.append(tok.value)
                op_positions.append(self._tok_pos(tok))
                self._advance()
                while True:
                    ntok = self._peek()
                    if ntok and ntok.kind == "OP" and ntok.value == "\n":
                        self._advance()
                        self._consume_pending_heredocs()
                        continue
                    break
                pipeline, lst_pipeline = self.parse_pipeline()
                pipelines.append(pipeline)
                lst_pipelines.append(lst_pipeline)
                continue
            break
        return (
            AndOr(pipelines=pipelines, operators=operators),
            LstAndOr(pipelines=lst_pipelines, operators=operators, op_positions=op_positions),
        )

    def parse_pipeline(self) -> tuple[Pipeline, LstPipeline]:
        negate = False
        while True:
            tok = self._peek()
            if not (self._is_word(tok) and tok.value == "!"):
                break
            self._advance()
            negate = not negate
        ntok = self._peek()
        if ntok is None or (ntok.kind == "OP" and ntok.value in ["\n", ";", "&", "|"]):
            # Accept lone `!`/`! !` as negation of a no-op command.
            null_cmd = SimpleCommand(argv=[Word(":")], assignments=[], redirects=[])
            lst_null_cmd = LstSimpleCommand(
                argv=[self._resolve_word(parse_word(":"))],
                assignments=[],
                redirects=[],
            )
            return Pipeline(commands=[null_cmd], negate=negate), LstPipeline(
                commands=[lst_null_cmd], negate=negate, op_positions=[]
            )
        command, lst_command = self.parse_command()
        commands: List[Command] = [command]
        lst_commands: List[LstCommand] = [lst_command]
        op_positions: List[LstTokenPos] = []
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "|":
                op_positions.append(self._tok_pos(tok))
                self._advance()
                while True:
                    ntok = self._peek()
                    if ntok and ntok.kind == "OP" and ntok.value == "\n":
                        self._advance()
                        self._consume_pending_heredocs()
                        continue
                    break
                command, lst_command = self.parse_command()
                commands.append(command)
                lst_commands.append(lst_command)
                continue
            break
        return (
            Pipeline(commands=commands, negate=negate),
            LstPipeline(commands=lst_commands, negate=negate, op_positions=op_positions),
        )

    def parse_command(self) -> tuple[Command, LstCommand]:
        alias_seen: set[str] = set()
        while True:
            tok0 = self._peek()
            if self._maybe_expand_alias(tok0, alias_seen, syntax_only=True):
                continue
            break
        tok = self._peek()
        tok1 = self._peek_n(1)
        if (
            tok
            and tok.kind == "OP"
            and tok.value == "(("
        ):
            if self._looks_like_arith_command():
                return self.parse_arith_command()
        if (
            tok
            and tok1
            and ((tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("))
            and ((tok1.kind == "OP" and tok1.value == "(") or (self._is_word(tok1) and tok1.value == "("))
            and self._token_adjacent(tok, tok1)
        ):
            if self._looks_like_arith_command():
                return self.parse_arith_command()
        if self._is_word(tok) and tok.value == "!":
            ntok = self._peek_n(1)
            if ntok is None or (ntok.kind == "OP" and ntok.value in ["\n", ";", "&", "|"]):
                self._advance()
                null_cmd = SimpleCommand(argv=[Word(":")], assignments=[], redirects=[])
                lst_null_cmd = LstSimpleCommand(
                    argv=[self._resolve_word(parse_word(":"))],
                    assignments=[],
                    redirects=[],
                )
                return null_cmd, lst_null_cmd
        if self._is_word(tok) and tok.value == "if":
            command, lst_command = self.parse_if()
            return self._maybe_wrap_redirects(command, lst_command)
        if self._is_word(tok) and tok.value in ["while", "until"]:
            command, lst_command = self.parse_while()
            return self._maybe_wrap_redirects(command, lst_command)
        if self._is_word(tok) and tok.value == "for":
            command, lst_command = self.parse_for()
            return self._maybe_wrap_redirects(command, lst_command)
        if self._is_word(tok) and tok.value == "select":
            command, lst_command = self.parse_select()
            return self._maybe_wrap_redirects(command, lst_command)
        if self._is_word(tok) and tok.value == "case":
            command, lst_command = self.parse_case()
            return self._maybe_wrap_redirects(command, lst_command)
        if self._is_word(tok) and tok.value == "coproc":
            command, lst_command = self.parse_coproc()
            return self._maybe_wrap_redirects(command, lst_command)
        if tok and ((tok.kind == "OP" and tok.value == "{") or (self._is_word(tok) and tok.value == "{")):
            command, lst_command = self.parse_group()
            return self._maybe_wrap_redirects(command, lst_command)
        if tok and ((tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "(")):
            command, lst_command = self.parse_subshell()
            return self._maybe_wrap_redirects(command, lst_command)
        if not (self._is_word(tok) and tok.value == "PYTHON") and self._looks_like_function_def():
            command, lst_command = self.parse_function_def()
            return self._maybe_wrap_redirects(command, lst_command)

        argv: List[Word] = []
        lst_argv: List = []
        assignments: List[Assignment] = []
        lst_assignments: List[LstAssignment] = []
        redirects: List[Redirect] = []
        lst_redirects: List[LstRedirect] = []
        command_line: int | None = None
        while True:
            tok = self._peek()
            if tok is None:
                break
            if (
                not argv
                and not assignments
                and tok.kind == "WORD"
                and tok.value.endswith("()")
                and tok.value[:-2] in RESERVED_WORDS
            ):
                raise ParseError(f'syntax error: unexpected "{tok.value[:-2]}" at {self._where(tok)}')
            if not argv and not assignments and self._is_word(tok) and tok.value in RESERVED_WORDS:
                tok1 = self._peek_n(1)
                tok2 = self._peek_n(2)
                has_paren_suffix = tok1 is not None and self._is_word(tok1) and tok1.value == "()"
                has_split_parens = False
                if tok1 is not None and tok2 is not None:
                    open_ok = (self._is_word(tok1) and tok1.value == "(") or (tok1.kind == "OP" and tok1.value == "(")
                    close_ok = (self._is_word(tok2) and tok2.value == ")") or (tok2.kind == "OP" and tok2.value == ")")
                    has_split_parens = open_ok and close_ok
                if has_paren_suffix or has_split_parens:
                    raise ParseError(f'syntax error: unexpected "{tok.value}" at {self._where(tok)}')
            in_dbl_bracket = bool(argv) and argv[0].text == "[["
            if in_dbl_bracket:
                if self._is_word(tok):
                    argv.append(Word(tok.value))
                    lst_argv.append(
                        self._resolve_word(parse_word(tok.value, line=tok.line, col=tok.col, index=tok.index))
                    )
                    self._advance()
                    if tok.value == "]]":
                        break
                    continue
                if tok.kind == "OP":
                    if tok.value in ["\n", ";", "&"]:
                        break
                    argv.append(Word(tok.value))
                    lst_argv.append(self._resolve_word(parse_word(tok.value, line=tok.line, col=tok.col, index=tok.index)))
                    self._advance()
                    continue
            if self._is_word(tok) and tok.value.isdigit():
                next_tok = self._peek_n(1)
                if (
                    next_tok
                    and next_tok.kind == "OP"
                    and next_tok.value in ["<", ">", ">>", "<>", "<<", "<<-", "<<<", ">&", "<&"]
                    and self._token_adjacent(tok, next_tok)
                ):
                    fd = int(tok.value)
                    if command_line is None:
                        command_line = tok.line
                    self._advance()
                    op_tok = self._advance()
                    target_tok = self._peek()
                    if target_tok is None or not self._is_word(target_tok):
                        raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                    redir = self._make_redirect(op_tok.value, target_tok.value, fd)
                    lst_redir = self._make_lst_redirect(op_tok, target_tok, fd)
                    self._advance()
                    if redir.op == "<<":
                        self.pending_heredocs.append((redir, lst_redir))
                    redirects.append(redir)
                    lst_redirects.append(lst_redir)
                    continue
            if tok.kind == "OP" and tok.value == "&":
                next_tok = self._peek_n(1)
                if (
                    next_tok
                    and next_tok.kind == "OP"
                    and next_tok.value in [">", ">>"]
                    and self._token_adjacent(tok, next_tok)
                ):
                    if command_line is None:
                        command_line = tok.line
                    self._advance()
                    self._advance()
                    target_tok = self._peek()
                    if target_tok is None or not self._is_word(target_tok):
                        raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                    op = "&>" if next_tok.value == ">" else "&>>"
                    redir = self._make_redirect(op, target_tok.value, None)
                    lst_redir = LstRedirect(
                        op=op,
                        target=self._resolve_word(
                            parse_word(target_tok.value, line=target_tok.line, col=target_tok.col, index=target_tok.index)
                        ),
                        fd=None,
                        op_pos=LstTokenPos(value=op, line=tok.line, col=tok.col, length=len(op), index=tok.index),
                    )
                    self._advance()
                    redirects.append(redir)
                    lst_redirects.append(lst_redir)
                    continue
            if tok.kind == "OP" and tok.value in ["<", ">", ">>", "<>", "<<", "<<-", "<<<", ">&", "<&"]:
                op = tok.value
                if command_line is None:
                    command_line = tok.line
                self._advance()
                target_tok = self._peek()
                if target_tok is None or not self._is_word(target_tok):
                    raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                redir = self._make_redirect(op, target_tok.value, None)
                lst_redir = self._make_lst_redirect(tok, target_tok, None)
                self._advance()
                if redir.op in ["<<", "<<-"]:
                    self.pending_heredocs.append((redir, lst_redir))
                redirects.append(redir)
                lst_redirects.append(lst_redir)
                continue
            if self._is_word(tok):
                if command_line is None:
                    command_line = tok.line
                if self._is_assignment(tok.value) and not argv:
                    name, op, value = self._split_assignment(tok.value)
                    self._advance()
                    if value == "":
                        comp = self._parse_compound_assignment_rhs()
                        if comp is not None:
                            value = comp
                    assignments.append(Assignment(name=name, value=value, op=op))
                    lst_assignments.append(
                        LstAssignment(
                            name=name,
                            value=self._resolve_word(
                                parse_word(value, line=tok.line, col=tok.col, index=tok.index)
                            ),
                            op=op,
                        )
                    )
                    continue
                else:
                    word_text = tok.value
                    word_line, word_col, word_index = tok.line, tok.col, tok.index
                    self._advance()
                    if (
                        argv
                        and argv[0].text in {"declare", "typeset", "local", "readonly", "export"}
                        and self._is_assignment(word_text)
                    ):
                        _, _, rhs = self._split_assignment(word_text)
                        if rhs == "":
                            comp = self._parse_compound_assignment_rhs()
                            if comp is not None:
                                word_text = word_text + comp
                        elif rhs.startswith("("):
                            depth = rhs.count("(") - rhs.count(")")
                            while depth > 0:
                                cur = self._peek()
                                if cur is None or (cur.kind == "OP" and cur.value == "\n"):
                                    raise ParseError("syntax error: missing ')' in compound assignment")
                                word_text = word_text + " " + cur.value
                                depth += cur.value.count("(") - cur.value.count(")")
                                self._advance()
                    argv.append(Word(word_text))
                    lst_argv.append(
                        self._resolve_word(
                            parse_word(word_text, line=word_line, col=word_col, index=word_index)
                        )
                    )
                continue
            break
        if not argv and not assignments and not redirects:
            if tok is not None and tok.kind == "OP":
                raise ParseError(f'syntax error: unexpected "{tok.value}" at {self._where(tok)}')
            raise ParseError(f"expected command at {self._where(tok)}")
        simple_cmd = SimpleCommand(argv=argv, assignments=assignments, redirects=redirects, line=command_line)
        lst_simple_cmd = LstSimpleCommand(argv=lst_argv, assignments=lst_assignments, redirects=lst_redirects)
        if argv and argv[0].text == "PYTHON":
            return self._parse_python_block_command(
                simple_cmd,
                lst_simple_cmd,
                tok,
            )
        if not argv and assignments:
            return simple_cmd, LstShAssignmentCommand(assignments=lst_assignments, redirects=lst_redirects)
        return simple_cmd, lst_simple_cmd

    def _looks_like_arith_command(self) -> bool:
        """Heuristic disambiguation for command form `(( ... ))`.

        In shell grammar this token prefix is ambiguous with nested subshell/grouping
        forms like `((echo x); echo y)`. Keep arithmetic parsing only when there is
        no top-level list separator before the matching closing `))`.
        """
        tok0 = self._peek_n(0)
        depth = 1
        arith_paren = 0
        i = 1 if (tok0 is not None and tok0.kind == "OP" and tok0.value == "((") else 2
        while True:
            tok = self._peek_n(i)
            if tok is None:
                return True
            tok1 = self._peek_n(i + 1)
            if (tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("):
                arith_paren += 1
                i += 1
                continue
            if tok.kind == "OP" and tok.value == "((":
                depth += 1
                i += 1
                continue
            if (
                tok1
                and ((tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("))
                and ((tok1.kind == "OP" and tok1.value == "(") or (self._is_word(tok1) and tok1.value == "("))
            ):
                depth += 1
                i += 2
                continue
            if tok.kind == "OP" and tok.value == "))":
                if arith_paren > 0:
                    arith_paren -= 1
                    i += 1
                    continue
                depth -= 1
                if depth == 0:
                    return True
                i += 1
                continue
            if (
                tok1
                and ((tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")"))
                and ((tok1.kind == "OP" and tok1.value == ")") or (self._is_word(tok1) and tok1.value == ")"))
            ):
                if arith_paren > 0:
                    arith_paren -= 1
                    i += 1
                    continue
                depth -= 1
                if depth == 0:
                    return True
                i += 2
                continue
            if (tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")"):
                if arith_paren > 0:
                    arith_paren -= 1
                i += 1
                continue
            if depth == 1 and tok.kind == "OP" and tok.value in {";", "\n", "&", "|"}:
                return False
            i += 1

    def parse_arith_command(self) -> tuple[SimpleCommand, LstSimpleCommand]:
        # Parse arithmetic command form: (( expr ))
        open_tok = self._peek()
        if open_tok is not None and open_tok.kind == "OP" and open_tok.value == "((":
            self._advance()
        else:
            self._expect_group_token("(")
            self._expect_group_token("(")
        parts: List[str] = []
        depth = 1
        arith_paren = 0
        while True:
            tok = self._peek()
            if tok is None:
                raise ParseError("syntax error: expected '))'")
            tok1 = self._peek_n(1)
            if (tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("):
                arith_paren += 1
                self._advance()
                parts.append(tok.value)
                continue
            if tok.kind == "OP" and tok.value == "((":
                depth += 1
                parts.append("((")
                self._advance()
                continue
            if (
                tok1
                and ((tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("))
                and ((tok1.kind == "OP" and tok1.value == "(") or (self._is_word(tok1) and tok1.value == "("))
            ):
                depth += 1
                parts.append("((")
                self._advance()
                self._advance()
                continue
            if (
                tok1
                and ((tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")"))
                and ((tok1.kind == "OP" and tok1.value == ")") or (self._is_word(tok1) and tok1.value == ")"))
            ):
                if arith_paren > 0:
                    arith_paren -= 1
                    self._advance()
                    parts.append(tok.value)
                    continue
                depth -= 1
                self._advance()
                self._advance()
                if depth == 0:
                    break
                parts.append("))")
                continue
            if tok.kind == "OP" and tok.value == "))":
                if arith_paren > 0:
                    arith_paren -= 1
                    self._advance()
                    parts.append(")")
                    continue
                depth -= 1
                self._advance()
                if depth == 0:
                    break
                parts.append("))")
                continue
            if (tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")"):
                if arith_paren > 0:
                    arith_paren -= 1
            self._advance()
            parts.append(tok.value)
        # Preserve arithmetic token adjacency so `(( x == 4 ))` becomes `x==4`
        # and is passed to `let` as a single expression argument.
        expr = "".join(parts)
        argv = [Word("let"), Word(expr)]
        lst_argv = [self._resolve_word(parse_word("let")), self._resolve_word(parse_word(expr))]
        return (
            SimpleCommand(argv=argv, assignments=[], redirects=[]),
            LstSimpleCommand(argv=lst_argv, assignments=[], redirects=[]),
        )

    def _parse_python_block_command(
        self,
        cmd: SimpleCommand,
        lst_cmd: LstSimpleCommand,
        separator_tok: Token | None,
    ) -> tuple[Command, LstCommand]:
        if separator_tok is None or separator_tok.kind != "OP" or separator_tok.value != "\n":
            raise ParseError(f"syntax error: PYTHON block requires newline before body at {self._where(separator_tok)}")
        self._advance()  # consume newline after PYTHON header
        self._consume_pending_heredocs()
        try:
            body = self.reader.consume_verbatim_block("END_PYTHON")
        except LexError as e:
            raise ParseError(str(e))

        cmd.argv = [Word("py")] + cmd.argv[1:]
        py_block_redir = Redirect(
            op="<<",
            target="__MCTASH_PY_BLOCK__",
            fd=0,
            here_doc=body,
            here_doc_expand=False,
        )
        cmd.redirects.append(py_block_redir)

        lst_cmd.argv = [self._resolve_word(parse_word("py"))] + lst_cmd.argv[1:]
        lst_cmd.redirects.append(
            LstRedirect(
                op="<<",
                target=self._resolve_word(parse_word("__MCTASH_PY_BLOCK__")),
                fd=0,
                here_doc=body,
                here_doc_expand=False,
            )
        )
        return cmd, lst_cmd

    def _is_assignment(self, text: str) -> bool:
        if "=" not in text:
            return False
        eq = text.find("=")
        if eq <= 0:
            return False
        lhs = text[:eq]
        if not lhs:
            return False
        if lhs.endswith("+"):
            lhs = lhs[:-1]
            if not lhs:
                return False
        # Plain NAME=VALUE
        if "[" not in lhs:
            if not (lhs[0].isalpha() or lhs[0] == "_"):
                return False
            return all(ch.isalnum() or ch == "_" for ch in lhs)

        # Extended bash form: NAME[SUBSCRIPT]=VALUE
        lb = lhs.find("[")
        rb = lhs.rfind("]")
        if lb <= 0 or rb != len(lhs) - 1:
            return False
        name = lhs[:lb]
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        if not all(ch.isalnum() or ch == "_" for ch in name):
            return False
        # Keep subscript syntax recognition conservative enough to avoid
        # misclassifying clearly invalid shell words (e.g. nested unquoted
        # brackets) as assignment words in ash/POSIX lanes.
        depth = 0
        max_depth = 0
        i = lb
        in_single = False
        in_double = False
        while i < len(lhs):
            ch = lhs[i]
            if in_single:
                if ch == "'":
                    in_single = False
                i += 1
                continue
            if in_double:
                if ch == "\\" and i + 1 < len(lhs):
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
            if ch == "[":
                depth += 1
                if depth > max_depth:
                    max_depth = depth
            elif ch == "]":
                depth -= 1
                if depth < 0:
                    return False
            i += 1
        if depth != 0:
            return False
        # NAME[SUB]= is valid; nested bracket structure is not parsed as an
        # assignment token here.
        return max_depth <= 1

    def _split_assignment(self, text: str) -> tuple[str, str, str]:
        eq = text.find("=")
        name = text[:eq]
        value = text[eq + 1 :]
        op = "="
        if name.endswith("+"):
            op = "+="
            name = name[:-1]
        return name, op, value

    def _parse_compound_assignment_rhs(self) -> str | None:
        tok = self._peek()
        if tok is None:
            return None
        if tok.kind == "WORD" and tok.value.startswith("("):
            src = self.reader.source
            start_index = tok.index
            i = start_index
            depth = 0
            while i < len(src):
                ch = src[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end_index = i + 1
                        while True:
                            cur = self._peek()
                            if cur is None or cur.index >= end_index:
                                break
                            self._advance()
                        return src[start_index:end_index]
                elif ch == "\n" and depth > 0:
                    raise ParseError("syntax error: missing ')' in compound assignment")
                i += 1
            raise ParseError("syntax error: missing ')' in compound assignment")
        if tok.kind != "OP" or tok.value != "(":
            return None
        start_index = tok.index
        self._advance()  # '('
        depth = 1
        while True:
            cur = self._peek()
            if cur is None:
                raise ParseError("syntax error: missing ')' in compound assignment")
            if cur.kind == "OP" and cur.value == "(":
                depth += 1
                self._advance()
                continue
            if cur.kind == "OP" and cur.value == ")":
                depth -= 1
                if depth == 0:
                    end_index = cur.index + len(cur.value)
                    self._advance()
                    return self.reader.source[start_index:end_index]
                self._advance()
                continue
            if cur.kind == "OP" and cur.value == "\n":
                raise ParseError(f"syntax error: missing ')' in compound assignment at {self._where(cur)}")
            self._advance()

    def _make_redirect(self, op: str, target: str, fd: int | None) -> Redirect:
        if op == "<<-":
            return Redirect(op="<<", target=target, fd=fd, here_doc_strip_tabs=True)
        return Redirect(op=op, target=target, fd=fd)

    def _make_lst_redirect(self, op_tok: Token, target_tok: Token, fd: int | None) -> LstRedirect:
        if op_tok.value == "<<-":
            return LstRedirect(
                op="<<",
                target=self._resolve_word(
                    parse_word(
                        target_tok.value,
                        line=target_tok.line,
                        col=target_tok.col,
                        index=target_tok.index,
                    )
                ),
                fd=fd,
                here_doc_strip_tabs=True,
                op_pos=self._tok_pos(op_tok),
            )
        return LstRedirect(
            op=op_tok.value,
            target=self._resolve_word(
                parse_word(
                    target_tok.value,
                    line=target_tok.line,
                    col=target_tok.col,
                    index=target_tok.index,
                )
            ),
            fd=fd,
            op_pos=self._tok_pos(op_tok),
        )

    def _apply_heredoc_token(self, redir: Redirect, lst_redir: LstRedirect, token_value: str) -> None:
        parts = token_value.split(":", 2)
        if len(parts) == 3:
            expand_flag, strip_flag, content = parts
            redir.here_doc_expand = expand_flag == "E"
            redir.here_doc_strip_tabs = strip_flag == "T"
            redir.here_doc = content
            lst_redir.here_doc_expand = expand_flag == "E"
            lst_redir.here_doc_strip_tabs = strip_flag == "T"
            lst_redir.here_doc = content
        else:
            redir.here_doc = token_value
            lst_redir.here_doc = token_value

    def parse_group(self) -> tuple[GroupCommand, LstGroupCommand]:
        self._expect_group_token("{")
        body, lst_body = self.parse_compound_list({"}"})
        self._expect_group_token("}")
        return GroupCommand(body=body), LstGroupCommand(body=lst_body)

    def parse_function_def(self) -> tuple[FunctionDef, LstFunctionDef]:
        tok0 = self._peek()
        saw_function_kw = False
        if tok0 and self._is_word(tok0) and tok0.value == "function":
            self._advance()
            saw_function_kw = True

        name_tok = self._advance()
        if name_tok is None or not self._is_word(name_tok):
            raise ParseError(f"expected function name at {self._where(name_tok)}")
        name = name_tok.value
        if name.endswith("()"):
            name = name[:-2]
        if name in RESERVED_WORDS:
            raise ParseError(f"expected function name at {self._where(name_tok)}")
        elif self._peek() and self._is_word(self._peek()) and self._peek().value == "()":
            self._advance()
        elif (
            self._peek()
            and self._peek().kind == "OP"
            and self._peek().value == "("
            and self._peek_n(1)
            and self._peek_n(1).kind == "OP"
            and self._peek_n(1).value == ")"
        ):
            # bash extension: optional () after function name even with `function` keyword
            self._advance()
            self._advance()
        elif not saw_function_kw:
            self._expect_group_token("(")
            self._expect_group_token(")")
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value in ["\n", ";"]:
                self._advance()
                if tok.value == "\n":
                    self._consume_pending_heredocs()
                continue
            break
        body_cmd, lst_body_cmd = self.parse_command()
        body, lst_body = self._command_as_list(body_cmd, lst_body_cmd)
        return FunctionDef(name=name, body=body), LstFunctionDef(name=name, body=lst_body)

    def _command_as_list(self, command: Command, lst_command: LstCommand) -> tuple[ListNode, LstListNode]:
        and_or = AndOr(pipelines=[Pipeline(commands=[command], negate=False)], operators=[])
        lst_and_or = LstAndOr(
            pipelines=[LstPipeline(commands=[lst_command], negate=False, op_positions=[])],
            operators=[],
            op_positions=[],
        )
        return (
            ListNode(items=[ListItem(node=and_or, background=False)]),
            LstListNode(items=[LstListItem(node=lst_and_or, terminator=None)]),
        )

    def parse_subshell(self) -> tuple[SubshellCommand, LstSubshellCommand]:
        self._expect_group_token("(")
        body, lst_body = self.parse_compound_list({")"})
        self._expect_group_token(")")
        return SubshellCommand(body=body), LstSubshellCommand(body=lst_body)

    def parse_for(self) -> tuple[ForCommand | ArithForCommand, LstForCommand | LstArithForCommand]:
        tok = self._advance()
        if tok is None or not self._is_word(tok) or tok.value != "for":
            raise ParseError(f"expected for at {self._where(tok)}")
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "\n":
                self._advance()
                continue
            break
        if self._looks_like_arith_for_header():
            init_expr, cond_expr, update_expr = self._parse_arith_for_header()
            while True:
                tok = self._peek()
                if tok and tok.kind == "OP" and tok.value in ["\n", ";"]:
                    self._advance()
                    if tok.value == "\n":
                        self._consume_pending_heredocs()
                    continue
                break
            do_tok = self._advance()
            if do_tok is None or not self._is_word(do_tok) or do_tok.value != "do":
                raise ParseError(f"expected do at {self._where(do_tok)}")
            body, lst_body = self.parse_compound_list({"done"})
            done_tok = self._advance()
            if done_tok is None or not self._is_word(done_tok) or done_tok.value != "done":
                raise ParseError(f"expected done at {self._where(done_tok)}")
            return (
                ArithForCommand(init=init_expr, cond=cond_expr, update=update_expr, body=body),
                LstArithForCommand(init=init_expr, cond=cond_expr, update=update_expr, body=LstDoGroup(body=lst_body)),
            )
        name_tok = self._advance()
        if name_tok is None or not self._is_word(name_tok):
            raise ParseError(f"expected name at {self._where(name_tok)}")
        items: List[Word] = []
        lst_items: List = []
        explicit_in = False
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "\n":
                self._advance()
                continue
            break

        tok = self._peek()
        if tok and self._is_word(tok) and tok.value == "in":
            explicit_in = True
            self._advance()
            while True:
                tok = self._peek()
                if tok is None:
                    break
                if tok.kind == "OP" and tok.value in [";", "\n"]:
                    break
                if self._is_word(tok):
                    items.append(Word(tok.value))
                    lst_items.append(
                        self._resolve_word(
                            parse_word(tok.value, line=tok.line, col=tok.col, index=tok.index)
                        )
                    )
                    self._advance()
                    continue
                break

        tok = self._peek()
        if tok and tok.kind == "OP" and tok.value == ";":
            self._advance()
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "\n":
                self._advance()
                continue
            break

        do_tok = self._advance()
        if do_tok is None or not self._is_word(do_tok) or do_tok.value != "do":
            raise ParseError(f"expected do at {self._where(do_tok)}")
        body, lst_body = self.parse_compound_list({"done"})
        done_tok = self._advance()
        if done_tok is None or not self._is_word(done_tok) or done_tok.value != "done":
            raise ParseError(f"expected done at {self._where(done_tok)}")
        return (
            ForCommand(name=name_tok.value, items=items, body=body, explicit_in=explicit_in),
            LstForCommand(
                name=name_tok.value,
                items=lst_items,
                body=LstDoGroup(body=lst_body),
                explicit_in=explicit_in,
            ),
        )

    def _looks_like_arith_for_header(self) -> bool:
        tok0 = self._peek()
        if tok0 is None:
            return False
        if tok0.kind == "OP" and tok0.value == "((":
            return True
        tok1 = self._peek_n(1)
        return (
            ((tok0.kind == "OP" and tok0.value == "(") or (self._is_word(tok0) and tok0.value == "("))
            and tok1 is not None
            and ((tok1.kind == "OP" and tok1.value == "(") or (self._is_word(tok1) and tok1.value == "("))
        )

    def _parse_arith_for_header(self) -> tuple[str, str, str]:
        open_tok = self._peek()
        if open_tok is not None and open_tok.kind == "OP" and open_tok.value == "((":
            self._advance()
        else:
            self._expect_group_token("(")
            self._expect_group_token("(")
        clauses: list[list[str]] = [[]]
        depth = 1
        arith_paren = 0
        while True:
            tok = self._peek()
            if tok is None:
                raise ParseError("syntax error: expected '))'")
            tok1 = self._peek_n(1)
            if (tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("):
                arith_paren += 1
                self._advance()
                clauses[-1].append(tok.value)
                continue
            if tok.kind == "OP" and tok.value == "((":
                depth += 1
                clauses[-1].append("((")
                self._advance()
                continue
            if (
                tok1
                and ((tok.kind == "OP" and tok.value == "(") or (self._is_word(tok) and tok.value == "("))
                and ((tok1.kind == "OP" and tok1.value == "(") or (self._is_word(tok1) and tok1.value == "("))
            ):
                depth += 1
                clauses[-1].append("((")
                self._advance()
                self._advance()
                continue
            if (
                tok1
                and ((tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")"))
                and ((tok1.kind == "OP" and tok1.value == ")") or (self._is_word(tok1) and tok1.value == ")"))
            ):
                if arith_paren > 0:
                    arith_paren -= 1
                    self._advance()
                    clauses[-1].append(tok.value)
                    continue
                depth -= 1
                self._advance()
                self._advance()
                if depth == 0:
                    break
                clauses[-1].append("))")
                continue
            if tok.kind == "OP" and tok.value == "))":
                if arith_paren > 0:
                    arith_paren -= 1
                    self._advance()
                    clauses[-1].append(")")
                    continue
                depth -= 1
                self._advance()
                if depth == 0:
                    break
                clauses[-1].append("))")
                continue
            if (tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")"):
                if arith_paren > 0:
                    arith_paren -= 1
            if depth == 1 and arith_paren == 0 and tok.kind == "OP" and tok.value == ";" and len(clauses) < 3:
                self._advance()
                clauses.append([])
                continue
            self._advance()
            clauses[-1].append(tok.value)
        while len(clauses) < 3:
            clauses.append([])
        init_expr = "".join(clauses[0]).strip()
        cond_expr = "".join(clauses[1]).strip()
        update_expr = "".join(clauses[2]).strip()
        return init_expr, cond_expr, update_expr

    def parse_select(self) -> tuple[SelectCommand, LstSelectCommand]:
        tok = self._advance()
        if tok is None or not self._is_word(tok) or tok.value != "select":
            raise ParseError(f"expected select at {self._where(tok)}")
        name_tok = self._advance()
        if name_tok is None or not self._is_word(name_tok):
            raise ParseError(f"expected name at {self._where(name_tok)}")
        if not self._is_valid_func_name(name_tok.value):
            raise ParseError(f"invalid select variable name at {self._where(name_tok)}")
        items: List[Word] = []
        lst_items: List = []
        explicit_in = False
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "\n":
                self._advance()
                continue
            break
        tok = self._peek()
        if tok and self._is_word(tok) and tok.value == "in":
            explicit_in = True
            self._advance()
            while True:
                tok = self._peek()
                if tok is None:
                    break
                if tok.kind == "OP" and tok.value in [";", "\n"]:
                    break
                if self._is_word(tok):
                    items.append(Word(tok.value))
                    lst_items.append(
                        self._resolve_word(
                            parse_word(tok.value, line=tok.line, col=tok.col, index=tok.index)
                        )
                    )
                    self._advance()
                    continue
                break
        tok = self._peek()
        if tok and tok.kind == "OP" and tok.value == ";":
            self._advance()
        while True:
            tok = self._peek()
            if tok and tok.kind == "OP" and tok.value == "\n":
                self._advance()
                continue
            break
        do_tok = self._advance()
        if do_tok is None or not self._is_word(do_tok) or do_tok.value != "do":
            raise ParseError(f"expected do at {self._where(do_tok)}")
        body, lst_body = self.parse_compound_list({"done"})
        done_tok = self._advance()
        if done_tok is None or not self._is_word(done_tok) or done_tok.value != "done":
            raise ParseError(f"expected done at {self._where(done_tok)}")
        return (
            SelectCommand(name=name_tok.value, items=items, body=body, explicit_in=explicit_in),
            LstSelectCommand(
                name=name_tok.value,
                items=lst_items,
                body=LstDoGroup(body=lst_body),
                explicit_in=explicit_in,
            ),
        )

    def parse_coproc(self) -> tuple[CoprocCommand, LstCoprocCommand]:
        tok = self._advance()
        if tok is None or not self._is_word(tok) or tok.value != "coproc":
            raise ParseError(f"expected coproc at {self._where(tok)}")
        name: str | None = None
        next_tok = self._peek()
        if (
            self._is_word(next_tok)
            and next_tok.value not in RESERVED_WORDS
            and self._is_valid_func_name(next_tok.value)
        ):
            lookahead = self._peek_n(1)
            if lookahead is not None:
                name = next_tok.value
                self._advance()
        child, lst_child = self.parse_command()
        return CoprocCommand(name=name, child=child), LstCoprocCommand(name=name, child=lst_child)

    def parse_case(self) -> tuple[CaseCommand, LstCaseCommand]:
        tok = self._advance()
        if tok is None or not self._is_word(tok) or tok.value != "case":
            raise ParseError(f"expected case at {self._where(tok)}")
        word_tok = self._advance()
        if word_tok is None or not self._is_word(word_tok):
            raise ParseError(f"expected case word at {self._where(word_tok)}")
        while True:
            sep = self._peek()
            if sep is None:
                break
            if sep.kind == "OP" and sep.value in {"\n", ";"}:
                self._advance()
                continue
            break
        in_tok = self._advance()
        if in_tok is None or not self._is_word(in_tok) or in_tok.value != "in":
            raise ParseError(f"expected in at {self._where(in_tok)}")
        items: List[CaseItem] = []
        lst_items: List[LstCaseItem] = []
        while True:
            tok = self._peek()
            if tok is None:
                break
            if self._is_word(tok) and tok.value == "esac":
                self._advance()
                break
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
                self._advance()
                continue
            if tok.kind == "OP" and tok.value == "(":
                self._advance()
            patterns: List[str] = []
            lst_patterns: List = []
            pat_parts: List[str] = []
            extglob_depth = 0
            while True:
                tok = self._peek()
                if tok is None:
                    break
                if self._is_word(tok) and tok.value == "esac" and not patterns and not pat_parts:
                    raise ParseError(f"syntax error near unexpected token `esac' at {self._where(tok)}")

                is_rparen = (tok.kind == "OP" and tok.value == ")") or (self._is_word(tok) and tok.value == ")")
                if is_rparen and extglob_depth == 0:
                    if pat_parts:
                        pat = "".join(pat_parts)
                        patterns.append(pat)
                        lst_patterns.append(self._resolve_word(parse_word(pat)))
                        pat_parts = []
                    self._advance()
                    break

                if tok.kind == "OP" and tok.value == "|" and extglob_depth == 0:
                    self._advance()
                    pat = "".join(pat_parts)
                    patterns.append(pat)
                    lst_patterns.append(self._resolve_word(parse_word(pat)))
                    pat_parts = []
                    continue

                val = tok.value
                if val == "(" and pat_parts and self._is_extglob_prefix_part(pat_parts[-1]):
                    extglob_depth += 1
                elif val == ")" and extglob_depth > 0:
                    extglob_depth -= 1
                pat_parts.append(val)
                self._advance()
            if self._looks_like_case_pattern_start():
                raise ParseError(f"syntax error: empty case action at {self._where(self._peek())}")
            body, lst_body = self.parse_compound_list({";;", ";&", ";;&", "esac"})
            tok = self._peek()
            if (
                (tok is None or (tok.kind == "OP" and tok.value == "\n"))
                and self._case_body_ends_with_bare_esac(body)
            ):
                raise ParseError("syntax error: expected clause terminator before esac")
            if (
                tok
                and self._is_word(tok)
                and tok.value == "esac"
                and self._last_token is not None
                and self._last_token.line == tok.line
                and not (self._last_token.kind == "OP" and self._last_token.value in [";", ";;", ";&", ";;&"])
            ):
                raise ParseError(f"syntax error: expected clause terminator before esac at {self._where(tok)}")
            op = ";;"
            if tok and tok.kind == "OP" and tok.value in {";;", ";&", ";;&"}:
                op = tok.value
                self._advance()
            elif tok and self._is_word(tok) and tok.value == "esac":
                op = "esac"
            items.append(CaseItem(patterns=patterns, body=body, op=op))
            lst_items.append(LstCaseItem(patterns=lst_patterns, body=lst_body, op=op))
        return (
            CaseCommand(value=Word(word_tok.value), items=items),
            LstCaseCommand(
                value=self._resolve_word(
                    parse_word(word_tok.value, line=word_tok.line, col=word_tok.col, index=word_tok.index)
                ),
                items=lst_items,
            ),
        )

    def _is_extglob_prefix_part(self, text: str) -> bool:
        if not text:
            return False
        return text in {"@", "!", "?", "+", "*"} or text.endswith(("@", "!", "?", "+", "*"))

    def _looks_like_case_pattern_start(self) -> bool:
        i = 0
        while True:
            tok = self._peek_n(i)
            if tok is None:
                return False
            if tok.kind == "OP" and tok.value in ["\n", ";"]:
                i += 1
                continue
            break
        if self._is_word(tok) and tok.value == "esac":
            return False
        tok1 = self._peek_n(i + 1)
        if tok1 and tok1.kind == "OP" and tok1.value in [")", "|"]:
            return True
        if self._is_word(tok) and tok.value.endswith("|"):
            return True
        return False

    def _case_body_ends_with_bare_esac(self, body: ListNode) -> bool:
        if not body.items:
            return False
        last_item = body.items[-1]
        andor = last_item.node
        if not andor.pipelines:
            return False
        pl = andor.pipelines[-1]
        if not pl.commands:
            return False
        cmd = pl.commands[-1]
        if not isinstance(cmd, SimpleCommand):
            return False
        if not cmd.argv:
            return False
        return cmd.argv[-1].text == "esac"

    def parse_if(self) -> tuple[IfCommand, LstIfCommand]:
        tok = self._advance()
        if tok is None or tok.value != "if":
            raise ParseError(f"expected if at {self._where(tok)}")
        cond, lst_cond = self.parse_compound_list({"then"})
        then_tok = self._advance()
        if then_tok is None or not self._is_word(then_tok) or then_tok.value != "then":
            raise ParseError(f"expected then at {self._where(then_tok)}")
        then_body, lst_then_body = self.parse_compound_list({"else", "elif", "fi"})
        elifs: List[tuple[ListNode, ListNode]] = []
        lst_elifs: List[tuple[LstListNode, LstListNode]] = []
        else_body = None
        lst_else_body = None
        while True:
            tok = self._peek()
            if tok and self._is_word(tok) and tok.value == "elif":
                self._advance()
                elif_cond, lst_elif_cond = self.parse_compound_list({"then"})
                then_tok = self._advance()
                if then_tok is None or not self._is_word(then_tok) or then_tok.value != "then":
                    raise ParseError(f"expected then at {self._where(then_tok)}")
                elif_body, lst_elif_body = self.parse_compound_list({"else", "elif", "fi"})
                elifs.append((elif_cond, elif_body))
                lst_elifs.append((lst_elif_cond, lst_elif_body))
                continue
            break
        tok = self._peek()
        if tok and self._is_word(tok) and tok.value == "else":
            self._advance()
            else_body, lst_else_body = self.parse_compound_list({"fi"})
        end_tok = self._advance()
        if end_tok is None or not self._is_word(end_tok) or end_tok.value != "fi":
            raise ParseError(f"expected fi at {self._where(end_tok)}")
        return (
            IfCommand(cond=cond, then_body=then_body, elifs=elifs, else_body=else_body),
            LstIfCommand(
                cond=lst_cond,
                then_body=lst_then_body,
                elifs=lst_elifs,
                else_body=lst_else_body,
            ),
        )

    def parse_while(self) -> tuple[WhileCommand, LstWhileCommand]:
        tok = self._advance()
        if tok is None or not self._is_word(tok) or tok.value not in ["while", "until"]:
            raise ParseError(f"expected while/until at {self._where(tok)}")
        until = tok.value == "until"
        cond, lst_cond = self.parse_compound_list({"do"})
        do_tok = self._advance()
        if do_tok is None or not self._is_word(do_tok) or do_tok.value != "do":
            raise ParseError(f"expected do at {self._where(do_tok)}")
        body, lst_body = self.parse_compound_list({"done"})
        done_tok = self._advance()
        if done_tok is None or not self._is_word(done_tok) or done_tok.value != "done":
            raise ParseError(f"expected done at {self._where(done_tok)}")
        return (
            WhileCommand(cond=cond, body=body, until=until),
            LstWhileCommand(cond=lst_cond, body=LstDoGroup(body=lst_body), until=until),
        )

    def _looks_like_function_def(self) -> bool:
        tok = self._peek()
        if tok is None or not self._is_word(tok):
            return False
        if tok.value == "function":
            tok1 = self._peek_n(1)
            return tok1 is not None and self._is_word(tok1)
        if tok.value.endswith("()"):
            base = tok.value[:-2]
            return self._is_valid_func_name(base)
        tok1 = self._peek_n(1)
        tok2 = self._peek_n(2)
        if tok1 and self._is_word(tok1) and tok1.value == "()":
            return self._is_valid_func_name(tok.value)
        if (
            tok1
            and ((self._is_word(tok1) and tok1.value == "(") or (tok1.kind == "OP" and tok1.value == "("))
            and tok2
            and ((self._is_word(tok2) and tok2.value == ")") or (tok2.kind == "OP" and tok2.value == ")"))
        ):
            return self._is_valid_func_name(tok.value)
        return False

    def _is_valid_func_name(self, name: str) -> bool:
        if not name:
            return False
        if name in RESERVED_WORDS:
            return False
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        return all(ch.isalnum() or ch == "_" for ch in name)

    def _resolve_word(self, word: LstWord) -> LstWord:
        word.parts = [self._resolve_part(part) for part in word.parts]
        return word

    def _resolve_part(self, part: LstWordPart) -> LstWordPart:
        if isinstance(part, LstCommandSubPart):
            if part.child is None:
                try:
                    part.child = Parser(part.source).parse_script().lst
                except ParseError:
                    part.child = None
            return part
        if isinstance(part, LstDoubleQuotedPart):
            part.parts = [self._resolve_part(p) for p in part.parts]
            return part
        if isinstance(part, LstLiteralPart) or isinstance(part, LstArithSubPart):
            return part
        return part

    def _tok_pos(self, tok: Token) -> LstTokenPos:
        return LstTokenPos(
            value=tok.value,
            line=tok.line,
            col=tok.col,
            length=len(tok.value),
            index=tok.index,
        )

    def _maybe_wrap_redirects(self, command: Command, lst_command: LstCommand) -> tuple[Command, LstCommand]:
        redirects: List[Redirect] = []
        lst_redirects: List[LstRedirect] = []
        while True:
            tok = self._peek()
            if tok is None:
                break
            if self._is_word(tok) and tok.value.isdigit():
                next_tok = self._peek_n(1)
                if (
                    next_tok
                    and next_tok.kind == "OP"
                    and next_tok.value in ["<", ">", ">>", "<>", "<<", "<<-", "<<<", ">&", "<&"]
                    and self._token_adjacent(tok, next_tok)
                ):
                    fd = int(tok.value)
                    self._advance()
                    op_tok = self._advance()
                    target_tok = self._peek()
                    if target_tok is None or not self._is_word(target_tok):
                        raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                    redir = self._make_redirect(op_tok.value, target_tok.value, fd)
                    lst_redir = self._make_lst_redirect(op_tok, target_tok, fd)
                    self._advance()
                    if redir.op in ["<<", "<<-"]:
                        self.pending_heredocs.append((redir, lst_redir))
                    redirects.append(redir)
                    lst_redirects.append(lst_redir)
                    continue
            if tok.kind == "OP" and tok.value == "&":
                next_tok = self._peek_n(1)
                if (
                    next_tok
                    and next_tok.kind == "OP"
                    and next_tok.value in [">", ">>"]
                    and self._token_adjacent(tok, next_tok)
                ):
                    self._advance()
                    self._advance()
                    target_tok = self._peek()
                    if target_tok is None or not self._is_word(target_tok):
                        raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                    op = "&>" if next_tok.value == ">" else "&>>"
                    redir = self._make_redirect(op, target_tok.value, None)
                    lst_redir = LstRedirect(
                        op=op,
                        target=self._resolve_word(
                            parse_word(target_tok.value, line=target_tok.line, col=target_tok.col, index=target_tok.index)
                        ),
                        fd=None,
                        op_pos=LstTokenPos(value=op, line=tok.line, col=tok.col, length=len(op), index=tok.index),
                    )
                    self._advance()
                    redirects.append(redir)
                    lst_redirects.append(lst_redir)
                    continue
            if tok.kind == "OP" and tok.value in ["<", ">", ">>", "<>", "<<", "<<-", "<<<", ">&", "<&"]:
                op_tok = tok
                self._advance()
                target_tok = self._peek()
                if target_tok is None or not self._is_word(target_tok):
                    raise ParseError(f"expected redirection target at {self._where(target_tok)}")
                redir = self._make_redirect(op_tok.value, target_tok.value, None)
                lst_redir = self._make_lst_redirect(op_tok, target_tok, None)
                self._advance()
                if redir.op in ["<<", "<<-"]:
                    self.pending_heredocs.append((redir, lst_redir))
                redirects.append(redir)
                lst_redirects.append(lst_redir)
                continue
            break
        if not redirects:
            return command, lst_command
        return RedirectCommand(child=command, redirects=redirects), LstRedirectCommand(
            child=lst_command, redirects=lst_redirects
        )

    def _consume_pending_heredocs(self) -> None:
        while self.pending_heredocs:
            tok = self._peek()
            if tok is None or tok.kind != "HEREDOC":
                break
            redir, lst_redir = self.pending_heredocs.pop(0)
            self._apply_heredoc_token(redir, lst_redir, tok.value)
            self._advance()


def parse(source: str) -> Script:
    return Parser(source).parse_script()
