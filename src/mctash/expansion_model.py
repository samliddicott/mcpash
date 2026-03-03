from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(frozen=True)
class ExpansionSegment:
    text: str
    quoted: bool
    glob_active: bool
    split_active: bool
    source_kind: str


@dataclass(frozen=True)
class ExpansionField:
    segments: List[ExpansionSegment] = field(default_factory=list)
    preserve_boundary: bool = False

    def text(self) -> str:
        return "".join(seg.text for seg in self.segments)


def fields_to_text_list(fields: Iterable[ExpansionField]) -> list[str]:
    return [f.text() for f in fields]
