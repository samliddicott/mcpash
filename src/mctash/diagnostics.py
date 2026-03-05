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
    INVALID_OPTION = "invalid_option"
    OPTION_REQUIRES_ARG = "option_requires_arg"
    INVALID_NUMBER = "invalid_number"
    INVALID_FD = "invalid_fd"
    TOO_MANY_ARGS = "too_many_args"
    NOT_VALID_IDENTIFIER = "not_valid_identifier"
    NOT_SHELL_BUILTIN = "not_shell_builtin"
    HELP_NO_TOPIC = "help_no_topic"
    DIRSTACK_EMPTY = "dirstack_empty"
    NO_OTHER_DIRECTORY = "no_other_directory"


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
        DiagnosticKey.INVALID_OPTION: "{cmd}: invalid option {opt}",
        DiagnosticKey.OPTION_REQUIRES_ARG: "{cmd}: option requires an argument -- {opt}",
        DiagnosticKey.INVALID_NUMBER: "{cmd}: invalid {what}",
        DiagnosticKey.INVALID_FD: "{cmd}: {fd}: invalid file descriptor",
        DiagnosticKey.TOO_MANY_ARGS: "{cmd}: too many arguments",
        DiagnosticKey.NOT_VALID_IDENTIFIER: "{cmd}: {name}: not a valid identifier",
        DiagnosticKey.NOT_SHELL_BUILTIN: "{cmd}: {name}: not a shell builtin",
        DiagnosticKey.HELP_NO_TOPIC: "{cmd}: no help topics match `{name}'",
        DiagnosticKey.DIRSTACK_EMPTY: "{cmd}: directory stack empty",
        DiagnosticKey.NO_OTHER_DIRECTORY: "{cmd}: no other directory",
    },
    "bash": {
        DiagnosticKey.COMMAND_NOT_FOUND: "{name}: command not found",
        DiagnosticKey.TYPE_NOT_FOUND: "type: {name}: not found",
        DiagnosticKey.READONLY_VAR: "{name}: readonly variable",
        DiagnosticKey.READONLY_UNSET: "{name}: cannot unset: readonly variable",
        DiagnosticKey.HASH_NOT_FOUND: "hash: {name}: not found",
        DiagnosticKey.ALIAS_NOT_FOUND: "alias: {name}: not found",
        DiagnosticKey.UNALIAS_NOT_FOUND: "unalias: {name}: not found",
        DiagnosticKey.INVALID_OPTION: "{cmd}: invalid option {opt}",
        DiagnosticKey.OPTION_REQUIRES_ARG: "{cmd}: option requires an argument -- {opt}",
        DiagnosticKey.INVALID_NUMBER: "{cmd}: invalid {what}",
        DiagnosticKey.INVALID_FD: "{cmd}: {fd}: invalid file descriptor",
        DiagnosticKey.TOO_MANY_ARGS: "{cmd}: too many arguments",
        DiagnosticKey.NOT_VALID_IDENTIFIER: "{cmd}: {name}: not a valid identifier",
        DiagnosticKey.NOT_SHELL_BUILTIN: "{cmd}: {name}: not a shell builtin",
        DiagnosticKey.HELP_NO_TOPIC: "{cmd}: no help topics match `{name}'",
        DiagnosticKey.DIRSTACK_EMPTY: "{cmd}: directory stack empty",
        DiagnosticKey.NO_OTHER_DIRECTORY: "{cmd}: no other directory",
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
