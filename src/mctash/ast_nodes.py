from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


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


@dataclass
class Command:
    argv: List[Word]
    assignments: List[Assignment]
    redirects: List[Redirect]


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
