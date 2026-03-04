from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class DiagnosticKey(str, Enum):
    COMMAND_NOT_FOUND = "command_not_found"
    TYPE_NOT_FOUND = "type_not_found"
    READONLY_VAR = "readonly_var"
    READONLY_UNSET = "readonly_unset"
    HASH_NOT_FOUND = "hash_not_found"
    ALIAS_NOT_FOUND = "alias_not_found"
    UNALIAS_NOT_FOUND = "unalias_not_found"


_TEMPLATES: dict[str, dict[DiagnosticKey, str]] = {
    # Initial templates intentionally keep current behavior.
    # Follow-up parity work can change bash templates independently.
    "ash": {
        DiagnosticKey.COMMAND_NOT_FOUND: "{name}: not found",
        DiagnosticKey.TYPE_NOT_FOUND: "type: {name}: not found",
        DiagnosticKey.READONLY_VAR: "{name}: is read only",
        DiagnosticKey.READONLY_UNSET: "{name}: is read only",
        DiagnosticKey.HASH_NOT_FOUND: "hash: {name}: not found",
        DiagnosticKey.ALIAS_NOT_FOUND: "alias: {name}: not found",
        DiagnosticKey.UNALIAS_NOT_FOUND: "unalias: {name}: not found",
    },
    "bash": {
        DiagnosticKey.COMMAND_NOT_FOUND: "{name}: command not found",
        DiagnosticKey.TYPE_NOT_FOUND: "type: {name}: not found",
        DiagnosticKey.READONLY_VAR: "{name}: readonly variable",
        DiagnosticKey.READONLY_UNSET: "{name}: cannot unset: readonly variable",
        DiagnosticKey.HASH_NOT_FOUND: "hash: {name}: not found",
        DiagnosticKey.ALIAS_NOT_FOUND: "alias: {name}: not found",
        DiagnosticKey.UNALIAS_NOT_FOUND: "unalias: {name}: not found",
    },
}


@dataclass
class DiagnosticCatalog:
    style: str
    gettext: Callable[[str], str]

    def render(self, key: DiagnosticKey, **kwargs: str) -> str:
        style = self.style if self.style in _TEMPLATES else "ash"
        template = _TEMPLATES[style].get(key) or _TEMPLATES["ash"][key]
        return self.gettext(template).format(**kwargs)
