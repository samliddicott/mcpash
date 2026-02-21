from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Word:
    text: str


@dataclass
class Assignment:
    name: str
    value: str


@dataclass
class Redirect:
    op: str  # "<", ">", ">>", "<<"
    target: str
    fd: Optional[int] = None
    here_doc: Optional[str] = None
    here_doc_expand: bool = True
    here_doc_strip_tabs: bool = False


@dataclass
class SimpleCommand:
    argv: List[Word]
    assignments: List[Assignment]
    redirects: List[Redirect]


@dataclass
class GroupCommand:
    body: "ListNode"


@dataclass
class IfCommand:
    cond: "ListNode"
    then_body: "ListNode"
    else_body: Optional["ListNode"]


@dataclass
class WhileCommand:
    cond: "ListNode"
    body: "ListNode"
    until: bool = False


@dataclass
class FunctionDef:
    name: str
    body: "ListNode"


Command = Union[SimpleCommand, GroupCommand, IfCommand, WhileCommand, FunctionDef]


@dataclass
class Pipeline:
    commands: List[Command]
    negate: bool = False


@dataclass
class AndOr:
    pipelines: List[Pipeline]
    operators: List[str]  # "&&" or "||"


@dataclass
class ListNode:
    items: List[AndOr]


@dataclass
class Script:
    body: ListNode
