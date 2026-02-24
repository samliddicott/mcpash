from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class LstWordPart:
    pass


@dataclass
class LstTokenPos:
    value: str
    line: int | None = None
    col: int | None = None
    length: int | None = None
    index: int | None = None


@dataclass
class LstLiteralPart(LstWordPart):
    text: str


@dataclass
class LstSingleQuotedPart(LstWordPart):
    text: str


@dataclass
class LstDoubleQuotedPart(LstWordPart):
    parts: List[LstWordPart]


@dataclass
class LstParamPart(LstWordPart):
    name: str


@dataclass
class LstCommandSubPart(LstWordPart):
    source: str
    child: "LstScript | None" = None
    style: str = "dollar"


@dataclass
class LstArithSubPart(LstWordPart):
    source: str


@dataclass
class LstBracedVarSubPart(LstWordPart):
    name: str
    op: str | None = None
    arg: "LstWord | None" = None


@dataclass
class LstWord:
    parts: List[LstWordPart]
    line: int | None = None
    col: int | None = None
    length: int | None = None
    index: int | None = None


@dataclass
class LstAssignment:
    name: str
    value: LstWord
    op: str = "="


@dataclass
class LstRedirect:
    op: str
    target: LstWord
    fd: Optional[int] = None
    here_doc: Optional[str] = None
    here_doc_expand: bool = True
    here_doc_strip_tabs: bool = False
    op_pos: Optional[LstTokenPos] = None


@dataclass
class LstSimpleCommand:
    argv: List[LstWord]
    assignments: List[LstAssignment]
    redirects: List[LstRedirect]


@dataclass
class LstRedirectCommand:
    child: "LstCommand"
    redirects: List[LstRedirect]


@dataclass
class LstGroupCommand:
    body: "LstListNode"


@dataclass
class LstIfCommand:
    cond: "LstListNode"
    then_body: "LstListNode"
    elifs: List[tuple["LstListNode", "LstListNode"]]
    else_body: Optional["LstListNode"]


@dataclass
class LstWhileCommand:
    cond: "LstListNode"
    body: "LstListNode"
    until: bool = False


@dataclass
class LstFunctionDef:
    name: str
    body: "LstListNode"


@dataclass
class LstSubshellCommand:
    body: "LstListNode"


@dataclass
class LstForCommand:
    name: str
    items: List[LstWord]
    body: "LstListNode"
    explicit_in: bool = False


@dataclass
class LstCaseItem:
    patterns: List[LstWord]
    body: "LstListNode"


@dataclass
class LstCaseCommand:
    value: LstWord
    items: List[LstCaseItem]


@dataclass
class LstControlFlowCommand:
    keyword: str
    arg: Optional[LstWord]


@dataclass
class LstShAssignmentCommand:
    assignments: List[LstAssignment]
    redirects: List[LstRedirect] = field(default_factory=list)


LstCommand = Union[
    LstSimpleCommand,
    LstRedirectCommand,
    LstGroupCommand,
    LstIfCommand,
    LstWhileCommand,
    LstFunctionDef,
    LstSubshellCommand,
    LstForCommand,
    LstCaseCommand,
    LstControlFlowCommand,
    LstShAssignmentCommand,
]


@dataclass
class LstPipeline:
    commands: List[LstCommand]
    negate: bool = False
    op_positions: List[LstTokenPos] = None


@dataclass
class LstAndOr:
    pipelines: List[LstPipeline]
    operators: List[str]
    op_positions: List[LstTokenPos] = None


@dataclass
class LstListItem:
    node: LstAndOr
    terminator: str | None = None


@dataclass
class LstListNode:
    items: List[LstListItem]


@dataclass
class LstScript:
    body: LstListNode
