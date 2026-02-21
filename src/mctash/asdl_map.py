from __future__ import annotations

from typing import Any, Dict, List, Optional

from .lst_nodes import (
    LstAndOr,
    LstArithSubPart,
    LstBracedVarSubPart,
    LstAssignment,
    LstCaseCommand,
    LstCaseItem,
    LstCommandSubPart,
    LstControlFlowCommand,
    LstDoubleQuotedPart,
    LstForCommand,
    LstFunctionDef,
    LstGroupCommand,
    LstIfCommand,
    LstListNode,
    LstLiteralPart,
    LstParamPart,
    LstPipeline,
    LstRedirect,
    LstRedirectCommand,
    LstScript,
    LstShAssignmentCommand,
    LstSingleQuotedPart,
    LstSimpleCommand,
    LstSubshellCommand,
    LstWhileCommand,
    LstWord,
    LstWordPart,
    LstTokenPos,
)


def lst_script_to_asdl(script: LstScript) -> Dict[str, Any]:
    return {
        "type": "command.CommandList",
        "children": [_lst_andor_to_command(node) for node in script.body.items],
        "note": "partial mapping to Oil/OSH ASDL",
    }


def _lst_andor_to_command(node: LstAndOr) -> Dict[str, Any]:
    return {
        "type": "command.AndOr",
        "children": [_lst_pipeline_to_command(p) for p in node.pipelines],
        "ops": [token_pos(pos) for pos in (node.op_positions or [])],
    }


def _lst_pipeline_to_command(node: LstPipeline) -> Dict[str, Any]:
    return {
        "type": "command.Pipeline",
        "negated": node.negate,
        "children": [_lst_command_to_command(c) for c in node.commands],
        "ops": [token_pos(pos) for pos in (node.op_positions or [])],
    }


def _lst_command_to_command(node) -> Dict[str, Any]:
    if isinstance(node, LstSimpleCommand):
        return _simple_command(node)
    if isinstance(node, LstRedirectCommand):
        return {
            "type": "command.Redirect",
            "child": _lst_command_to_command(node.child),
            "redirects": [_redir(r) for r in node.redirects],
        }
    if isinstance(node, LstGroupCommand):
        return {
            "type": "command.BraceGroup",
            "children": [_lst_andor_to_command(n) for n in node.body.items],
        }
    if isinstance(node, LstIfCommand):
        return _if_command(node)
    if isinstance(node, LstWhileCommand):
        return _while_command(node)
    if isinstance(node, LstFunctionDef):
        return {
            "type": "command.ShFunction",
            "name": node.name,
            "body": _lst_andor_list(node.body),
        }
    if isinstance(node, LstSubshellCommand):
        return {
            "type": "command.Subshell",
            "child": _lst_andor_list(node.body),
            "is_last_cmd": False,
        }
    if isinstance(node, LstForCommand):
        return _for_command(node)
    if isinstance(node, LstCaseCommand):
        return _case_command(node)
    if isinstance(node, LstControlFlowCommand):
        return {
            "type": "command.ControlFlow",
            "keyword": token(node.keyword),
            "arg_word": word(node.arg) if node.arg else None,
        }
    if isinstance(node, LstShAssignmentCommand):
        return {
            "type": "command.ShAssignment",
            "pairs": [_env_pair(a) for a in node.assignments],
        }
    return {"type": "command.NoOp"}


def _lst_andor_list(node: LstListNode) -> Dict[str, Any]:
    return {
        "type": "command.CommandList",
        "children": [_lst_andor_to_command(n) for n in node.items],
    }


def _simple_command(node: LstSimpleCommand) -> Dict[str, Any]:
    return {
        "type": "command.Simple",
        "more_env": [_env_pair(a) for a in node.assignments],
        "words": [word(w) for w in node.argv],
        "typed_args": None,
        "block": None,
        "is_last_cmd": False,
        "redirects": [_redir(r) for r in node.redirects] or None,
    }


def _env_pair(assign: LstAssignment) -> Dict[str, Any]:
    return {
        "type": "EnvPair",
        "name": assign.name,
        "val": {"type": "rhs_word.Compound", "word": word(assign.value)},
    }


def _redir(redir: LstRedirect) -> Dict[str, Any]:
    if redir.here_doc is not None:
        arg = {
            "type": "redir_param.HereDoc",
            "here_begin": word(redir.target),
            "stdin_parts": [word_part(LstLiteralPart(redir.here_doc))],
        }
    else:
        arg = {"type": "redir_param.Word", "word": word(redir.target)}
    return {
        "type": "Redir",
        "op": token_pos(redir.op_pos) if redir.op_pos else token(redir.op),
        "loc": {"fd": redir.fd},
        "arg": arg,
    }


def _if_command(node: LstIfCommand) -> Dict[str, Any]:
    arms = [{"cond": _lst_andor_list(node.cond), "action": _lst_andor_list(node.then_body)}]
    for cond, body in node.elifs:
        arms.append({"cond": _lst_andor_list(cond), "action": _lst_andor_list(body)})
    else_action = _lst_andor_list(node.else_body) if node.else_body else None
    return {
        "type": "command.If",
        "arms": arms,
        "else_action": else_action,
    }


def _while_command(node: LstWhileCommand) -> Dict[str, Any]:
    keyword = "until" if node.until else "while"
    return {
        "type": "command.WhileUntil",
        "keyword": token(keyword),
        "cond": _lst_andor_list(node.cond),
        "body": _lst_andor_list(node.body),
    }


def _for_command(node: LstForCommand) -> Dict[str, Any]:
    return {
        "type": "command.ForEach",
        "iter_names": [node.name],
        "iterable": {
            "type": "for_iter.Words",
            "words": [word(w) for w in node.items],
        },
        "body": _lst_andor_list(node.body),
    }


def _case_command(node: LstCaseCommand) -> Dict[str, Any]:
    return {
        "type": "command.Case",
        "to_match": {"type": "case_arg.Word", "word": word(node.value)},
        "arms": [_case_arm(item) for item in node.items],
    }


def _case_arm(item: LstCaseItem) -> Dict[str, Any]:
    return {
        "type": "CaseArm",
        "pattern": {"type": "pat.Words", "words": [word(p) for p in item.patterns]},
        "action": [_lst_andor_to_command(n) for n in item.body.items],
    }


def word(w: LstWord) -> Dict[str, Any]:
    return {
        "type": "word.Compound",
        "parts": [word_part(p) for p in w.parts],
        "pos": {
            "line": w.line,
            "col": w.col,
            "length": w.length,
            "index": w.index,
        },
    }


def word_part(part: LstWordPart) -> Dict[str, Any]:
    if isinstance(part, LstLiteralPart):
        return {"type": "word_part.Literal", "tval": part.text}
    if isinstance(part, LstSingleQuotedPart):
        return {"type": "word_part.SingleQuoted", "sval": part.text}
    if isinstance(part, LstDoubleQuotedPart):
        return {
            "type": "word_part.DoubleQuoted",
            "parts": [word_part(p) for p in part.parts],
        }
    if isinstance(part, LstParamPart):
        return {"type": "word_part.SimpleVarSub", "name": part.name}
    if isinstance(part, LstBracedVarSubPart):
        return {
            "type": "word_part.BracedVarSub",
            "name": part.name,
            "op": part.op,
            "arg": word(part.arg) if part.arg else None,
        }
    if isinstance(part, LstCommandSubPart):
        return {
            "type": "word_part.CommandSub",
            "child_source": part.source,
            "child": lst_script_to_asdl(part.child) if part.child else None,
        }
    if isinstance(part, LstArithSubPart):
        return {"type": "word_part.ArithSub", "expr_source": part.source}
    return {"type": "word_part.Literal", "tval": ""}


def token(tval: Optional[str]) -> Dict[str, Any]:
    return {"type": "Token", "tval": tval}


def token_pos(pos: LstTokenPos) -> Dict[str, Any]:
    return {
        "type": "Token",
        "tval": pos.value,
        "pos": {
            "line": pos.line,
            "col": pos.col,
            "length": pos.length,
            "index": pos.index,
        },
    }
