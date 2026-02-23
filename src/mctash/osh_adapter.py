from __future__ import annotations

from typing import Any, Dict, List

from .ast_nodes import (
    AndOr,
    Assignment,
    CaseCommand,
    CaseItem,
    ForCommand,
    FunctionDef,
    GroupCommand,
    IfCommand,
    ListItem,
    ListNode,
    Pipeline,
    Redirect,
    RedirectCommand,
    SimpleCommand,
    SubshellCommand,
    WhileCommand,
    Word,
)


class OshAdapterError(Exception):
    pass


def asdl_item_to_list_item(node: Dict[str, Any]) -> ListItem:
    if node.get("type") == "command.Sentence":
        child = node.get("child")
        if child is None:
            raise OshAdapterError("command.Sentence missing child")
        list_item = asdl_item_to_list_item(child)
        term = node.get("terminator")
        if _token_text(term) == "&":
            list_item.background = True
        return list_item
    if node.get("type") != "command.AndOr":
        raise OshAdapterError(f"expected command.AndOr list item, got {node.get('type')}")
    return ListItem(node=_asdl_andor(node), background=False)


def _asdl_andor(node: Dict[str, Any]) -> AndOr:
    pipelines = [_asdl_pipeline(p) for p in node.get("children", [])]
    ops = []
    for op in node.get("ops") or []:
        if isinstance(op, dict):
            value = _token_text(op)
        else:
            value = str(op)
        if value in ["&&", "||"]:
            ops.append(value)
    return AndOr(pipelines=pipelines, operators=ops)


def _asdl_pipeline(node: Dict[str, Any]) -> Pipeline:
    commands = [_asdl_command(c) for c in node.get("children", [])]
    return Pipeline(commands=commands, negate=bool(node.get("negated", False)))


def _asdl_command(node: Dict[str, Any]):
    t = node.get("type")
    if t == "command.Simple":
        argv = [Word(_word_to_text(w)) for w in node.get("words") or []]
        assignments = []
        for env_pair in node.get("more_env") or []:
            assignments.append(
                Assignment(
                    name=env_pair.get("name", ""),
                    value=_rhs_word_to_text(env_pair.get("val")),
                    op="=",
                )
            )
        redirects = [_asdl_redirect(r) for r in node.get("redirects") or []]
        return SimpleCommand(argv=argv, assignments=assignments, redirects=redirects, line=_command_line(node))
    if t == "command.Redirect":
        child = _asdl_command(node.get("child") or {})
        redirects = [_asdl_redirect(r) for r in node.get("redirects") or []]
        return RedirectCommand(child=child, redirects=redirects)
    if t == "command.BraceGroup":
        children = node.get("children") or []
        items: List[ListItem] = []
        for child in children:
            items.append(asdl_item_to_list_item(child))
        return GroupCommand(body=ListNode(items=items))
    if t == "command.Subshell":
        child = node.get("child") or {}
        return SubshellCommand(body=_asdl_command_list(child))
    if t == "command.If":
        arms = node.get("arms") or []
        if not arms:
            raise OshAdapterError("if command missing arms")
        first = arms[0]
        cond = _asdl_command_list(first.get("cond") or {})
        then_body = _asdl_command_list(first.get("action") or {})
        elifs = []
        for arm in arms[1:]:
            elifs.append(
                (
                    _asdl_command_list(arm.get("cond") or {}),
                    _asdl_command_list(arm.get("action") or {}),
                )
            )
        else_action = node.get("else_action")
        else_body = _asdl_command_list(else_action) if else_action else None
        return IfCommand(cond=cond, then_body=then_body, elifs=elifs, else_body=else_body)
    if t == "command.WhileUntil":
        kw = _token_text(node.get("keyword"))
        return WhileCommand(
            cond=_asdl_command_list(node.get("cond") or {}),
            body=_asdl_command_list(node.get("body") or {}),
            until=(kw == "until"),
        )
    if t == "command.ShFunction":
        return FunctionDef(name=node.get("name", ""), body=_asdl_command_list(node.get("body") or {}))
    if t == "command.ForEach":
        iterable = node.get("iterable") or {}
        words = [Word(_word_to_text(w)) for w in iterable.get("words") or []]
        names = node.get("iter_names") or [""]
        return ForCommand(name=names[0], items=words, body=_asdl_command_list(node.get("body") or {}))
    if t == "command.Case":
        to_match = node.get("to_match") or {}
        value_node = to_match.get("word") if isinstance(to_match, dict) else None
        value = Word(_word_to_text(value_node or {}))
        items = []
        for arm in node.get("arms") or []:
            pat = arm.get("pattern") or {}
            patterns = []
            for w in pat.get("words") or []:
                patterns.append(_word_to_text(w))
            action = arm.get("action") or []
            items.append(CaseItem(patterns=patterns, body=_asdl_action_list(action)))
        return CaseCommand(value=value, items=items)
    if t == "command.ControlFlow":
        keyword = _token_text(node.get("keyword"))
        argv = [Word(keyword or "")]
        arg = node.get("arg_word")
        if arg is not None:
            argv.append(Word(_word_to_text(arg)))
        return SimpleCommand(argv=argv, assignments=[], redirects=[], line=_command_line(node))
    if t == "command.ShAssignment":
        assignments = []
        for pair in node.get("pairs") or []:
            assignments.append(
                Assignment(
                    name=pair.get("name", ""),
                    value=_rhs_word_to_text(pair.get("rhs")),
                    op=pair.get("op", "="),
                )
            )
        redirects = [_asdl_redirect(r) for r in node.get("redirects") or []]
        return SimpleCommand(argv=[], assignments=assignments, redirects=redirects, line=_command_line(node))
    raise OshAdapterError(f"unsupported ASDL command node {t}")


def _asdl_command_list(node: Dict[str, Any]) -> ListNode:
    if node.get("type") != "command.CommandList":
        raise OshAdapterError(f"expected command.CommandList, got {node.get('type')}")
    items: List[ListItem] = []
    for child in node.get("children") or []:
        items.append(asdl_item_to_list_item(child))
    return ListNode(items=items)


def _asdl_action_list(action: List[Dict[str, Any]]) -> ListNode:
    items: List[ListItem] = []
    for child in action:
        items.append(asdl_item_to_list_item(child))
    return ListNode(items=items)


def _asdl_redirect(node: Dict[str, Any]) -> Redirect:
    op = node.get("op")
    op = _token_text(op) if isinstance(op, dict) else op
    strip_tabs = op == "<<-"
    if op == "<<-":
        op = "<<"
    loc = node.get("loc") or {}
    fd = loc.get("fd") if isinstance(loc, dict) else None
    arg = node.get("arg") or {}
    if arg.get("type") == "redir_param.HereDoc":
        begin = arg.get("here_begin") or {}
        target = _word_to_text(begin)
        parts = arg.get("stdin_parts") or []
        content = "".join(_word_part_to_heredoc_text(p) for p in parts)
        return Redirect(
            op=op or "<<",
            target=target,
            fd=fd,
            here_doc=content,
            here_doc_expand=bool(arg.get("do_expand", True)),
            here_doc_strip_tabs=bool(arg.get("strip_tabs", strip_tabs)),
        )
    target_word = arg.get("word") or {}
    return Redirect(op=op or ">", target=_word_to_text(target_word), fd=fd)


def _token_text(tok: Any) -> str:
    if isinstance(tok, dict):
        if "tval" in tok:
            return str(tok.get("tval") or "")
        if "value" in tok:
            return str(tok.get("value") or "")
        return ""
    if tok is None:
        return ""
    return str(tok)


def _rhs_word_to_text(node: Dict[str, Any] | None) -> str:
    if not node:
        return ""
    if node.get("type") == "rhs_word.Compound":
        return _word_to_text(node.get("word") or {})
    return ""


def _word_to_text(node: Dict[str, Any]) -> str:
    if not isinstance(node, dict):
        return ""
    if node.get("type") != "word.Compound":
        return ""
    return "".join(_word_part_to_text(p) for p in (node.get("parts") or []))


def _word_part_to_text(node: Dict[str, Any]) -> str:
    t = node.get("type")
    if t == "word_part.Literal":
        return node.get("tval", "")
    if t == "word_part.SingleQuoted":
        return "'" + node.get("sval", "") + "'"
    if t == "word_part.DoubleQuoted":
        inner = "".join(_word_part_to_double_text(p) for p in node.get("parts") or [])
        return '"' + inner + '"'
    if t == "word_part.SimpleVarSub":
        return "$" + node.get("name", "")
    if t == "word_part.BracedVarSub":
        name = node.get("name", "")
        op = node.get("op")
        if op == "__len__":
            return "${#" + name + "}"
        if op:
            arg = node.get("arg")
            arg_s = _word_to_text(arg) if isinstance(arg, dict) else ""
            return "${" + name + op + arg_s + "}"
        return "${" + name + "}"
    if t == "word_part.CommandSub":
        src = node.get("child_source") or ""
        escaped = src.replace("\\", "\\\\").replace("`", "\\`")
        return "`" + escaped + "`"
    if t == "word_part.ArithSub":
        return "$((" + (node.get("expr_source") or node.get("code") or "") + "))"
    return ""


def _word_part_to_double_text(node: Dict[str, Any]) -> str:
    t = node.get("type")
    if t == "word_part.Literal":
        return node.get("tval", "")
    # Other parts remain structural expansions inside double quotes.
    return _word_part_to_text(node)


def _word_part_to_heredoc_text(node: Dict[str, Any]) -> str:
    if node.get("type") == "word_part.Literal":
        return node.get("tval", "")
    return _word_part_to_text(node)


def _command_line(node: Dict[str, Any]) -> int | None:
    for w in node.get("words") or []:
        pos = w.get("pos") if isinstance(w, dict) else None
        if isinstance(pos, dict):
            line = pos.get("line")
            if isinstance(line, int):
                return line
    for r in node.get("redirects") or []:
        op = r.get("op") if isinstance(r, dict) else None
        if isinstance(op, dict):
            pos = op.get("pos")
            if isinstance(pos, dict):
                line = pos.get("line")
                if isinstance(line, int):
                    return line
    return None
