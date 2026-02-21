from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lst_nodes import LstScript


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
    elifs: List[tuple["ListNode", "ListNode"]]
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


@dataclass
class SubshellCommand:
    body: "ListNode"


@dataclass
class ForCommand:
    name: str
    items: List[Word]
    body: "ListNode"


@dataclass
class CaseItem:
    patterns: List[str]
    body: "ListNode"


@dataclass
class CaseCommand:
    value: Word
    items: List[CaseItem]


Command = Union[
    SimpleCommand,
    GroupCommand,
    IfCommand,
    WhileCommand,
    FunctionDef,
    SubshellCommand,
    ForCommand,
    CaseCommand,
]


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
    lst: Optional["LstScript"] = None
