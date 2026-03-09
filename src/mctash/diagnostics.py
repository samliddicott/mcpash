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
    ILLEGAL_OPTION = "illegal_option"
    NOT_IN_FUNCTION = "not_in_function"
    REQUIRES_BASH_COMPAT = "requires_bash_compat"
    BAD_VARIABLE_NAME = "bad_variable_name"
    USAGE_GETOPTS = "usage_getopts"
    SHOPT_CONFLICT = "shopt_conflict"
    SHOPT_INVALID_NAME = "shopt_invalid_name"
    USAGE_FROM_IMPORT = "usage_from_import"
    FROM_NOT_FOUND = "from_not_found"
    FROM_EXCEPTION = "from_exception"
    READ_ILLEGAL_OPTION = "read_illegal_option"
    READ_OPTION_REQUIRES_ARG = "read_option_requires_arg"
    READ_ILLEGAL_NUMBER = "read_illegal_number"
    READ_ILLEGAL_FD = "read_illegal_fd"
    READ_UNKNOWN_OPTION = "read_unknown_option"
    SHIFT_ILLEGAL_NUMBER = "shift_illegal_number"
    GETOPTS_ILLEGAL_OPTION = "getopts_illegal_option"
    GETOPTS_NO_ARG = "getopts_no_arg"
    BUILTIN_NOT_SHELL_BUILTIN = "builtin_not_shell_builtin"
    INVALID_SIGNAL_SPEC = "invalid_signal_spec"
    JOB_NOT_UNDER_CONTROL = "job_not_under_control"
    DECLARE_NOT_FOUND = "declare_not_found"
    SET_CANT_ACCESS_TTY = "set_cant_access_tty"
    UNSET_BAD_VARIABLE_NAME = "unset_bad_variable_name"
    ARITH_DIVIDE_BY_ZERO = "arith_divide_by_zero"
    ARITH_SYNTAX_ERROR = "arith_syntax_error"
    PERMISSION_DENIED = "permission_denied"
    PERMISSION_DENIED_NAME = "permission_denied_name"
    FILE_NAME_TOO_LONG_NAME = "file_name_too_long_name"
    ERRNO_NAME = "errno_name"
    PY_USAGE = "py_usage"
    UNALIAS_USAGE = "unalias_usage"
    WRITE_ERROR = "write_error"
    FC_USAGE = "fc_usage"
    FC_NO_HISTORY = "fc_no_history"
    FC_EVENT_NOT_FOUND = "fc_event_not_found"
    FC_INVALID_EDITOR = "fc_invalid_editor"
    FC_RECURSION_GUARD = "fc_recursion_guard"


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
        DiagnosticKey.ILLEGAL_OPTION: "illegal option {opt}",
        DiagnosticKey.NOT_IN_FUNCTION: "not in a function",
        DiagnosticKey.REQUIRES_BASH_COMPAT: "{feature} requires BASH_COMPAT to be set",
        DiagnosticKey.BAD_VARIABLE_NAME: "{name}: bad variable name",
        DiagnosticKey.USAGE_GETOPTS: "usage: getopts optstring var [arg ...]",
        DiagnosticKey.SHOPT_CONFLICT: "shopt: cannot set and unset in same invocation",
        DiagnosticKey.SHOPT_INVALID_NAME: "shopt: invalid shell option name: {name}",
        DiagnosticKey.USAGE_FROM_IMPORT: "usage: from MOD import NAME [as ALIAS]",
        DiagnosticKey.FROM_NOT_FOUND: "{name}: not found in module {module}",
        DiagnosticKey.FROM_EXCEPTION: "{etype}: {msg}",
        DiagnosticKey.READ_ILLEGAL_OPTION: "read: Illegal option {opt}",
        DiagnosticKey.READ_OPTION_REQUIRES_ARG: "read: option requires an argument -- {opt}",
        DiagnosticKey.READ_ILLEGAL_NUMBER: "read: Illegal number",
        DiagnosticKey.READ_ILLEGAL_FD: "read: Illegal file descriptor",
        DiagnosticKey.READ_UNKNOWN_OPTION: "read: unknown option {opt}",
        DiagnosticKey.SHIFT_ILLEGAL_NUMBER: "Illegal number: {value}",
        DiagnosticKey.GETOPTS_ILLEGAL_OPTION: "Illegal option -{opt}",
        DiagnosticKey.GETOPTS_NO_ARG: "No arg for -{opt} option",
        DiagnosticKey.BUILTIN_NOT_SHELL_BUILTIN: "builtin: {name}: not a shell builtin",
        DiagnosticKey.INVALID_SIGNAL_SPEC: "{sig}: invalid signal specification",
        DiagnosticKey.JOB_NOT_UNDER_CONTROL: "job {token} not created under job control",
        DiagnosticKey.DECLARE_NOT_FOUND: "not found: {name}",
        DiagnosticKey.SET_CANT_ACCESS_TTY: "set: can't access tty; job control turned off",
        DiagnosticKey.UNSET_BAD_VARIABLE_NAME: "-: bad variable name",
        DiagnosticKey.ARITH_DIVIDE_BY_ZERO: "divide by zero",
        DiagnosticKey.ARITH_SYNTAX_ERROR: "arithmetic syntax error",
        DiagnosticKey.PERMISSION_DENIED: ": Permission denied",
        DiagnosticKey.PERMISSION_DENIED_NAME: "{name}: Permission denied",
        DiagnosticKey.FILE_NAME_TOO_LONG_NAME: "{name}: File name too long",
        DiagnosticKey.ERRNO_NAME: "{name}: {error}",
        DiagnosticKey.PY_USAGE: "usage: {entry} [-e] [-x] [--no-dedent] [-v VAR] [-r VAR] [-t VAR] [-u VAR] [CODE]",
        DiagnosticKey.UNALIAS_USAGE: "unalias: usage: unalias [-a] name ...",
        DiagnosticKey.WRITE_ERROR: "ash: write error: {error}",
        DiagnosticKey.FC_USAGE: "usage: fc [-e ename] [-lnr] [first] [last] or fc -s [old=new] [command]",
        DiagnosticKey.FC_NO_HISTORY: "fc: no command found",
        DiagnosticKey.FC_EVENT_NOT_FOUND: "fc: event not found: {ref}",
        DiagnosticKey.FC_INVALID_EDITOR: "fc: invalid editor command",
        DiagnosticKey.FC_RECURSION_GUARD: "fc: recursive replay blocked",
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
        DiagnosticKey.ILLEGAL_OPTION: "illegal option {opt}",
        DiagnosticKey.NOT_IN_FUNCTION: "not in a function",
        DiagnosticKey.REQUIRES_BASH_COMPAT: "{feature} requires BASH_COMPAT to be set",
        DiagnosticKey.BAD_VARIABLE_NAME: "{name}: bad variable name",
        DiagnosticKey.USAGE_GETOPTS: "usage: getopts optstring var [arg ...]",
        DiagnosticKey.SHOPT_CONFLICT: "shopt: cannot set and unset in same invocation",
        DiagnosticKey.SHOPT_INVALID_NAME: "shopt: invalid shell option name: {name}",
        DiagnosticKey.USAGE_FROM_IMPORT: "usage: from MOD import NAME [as ALIAS]",
        DiagnosticKey.FROM_NOT_FOUND: "{name}: not found in module {module}",
        DiagnosticKey.FROM_EXCEPTION: "{etype}: {msg}",
        DiagnosticKey.READ_ILLEGAL_OPTION: "read: Illegal option {opt}",
        DiagnosticKey.READ_OPTION_REQUIRES_ARG: "read: option requires an argument -- {opt}",
        DiagnosticKey.READ_ILLEGAL_NUMBER: "read: Illegal number",
        DiagnosticKey.READ_ILLEGAL_FD: "read: Illegal file descriptor",
        DiagnosticKey.READ_UNKNOWN_OPTION: "read: unknown option {opt}",
        DiagnosticKey.SHIFT_ILLEGAL_NUMBER: "Illegal number: {value}",
        DiagnosticKey.GETOPTS_ILLEGAL_OPTION: "Illegal option -{opt}",
        DiagnosticKey.GETOPTS_NO_ARG: "No arg for -{opt} option",
        DiagnosticKey.BUILTIN_NOT_SHELL_BUILTIN: "builtin: {name}: not a shell builtin",
        DiagnosticKey.INVALID_SIGNAL_SPEC: "{sig}: invalid signal specification",
        DiagnosticKey.JOB_NOT_UNDER_CONTROL: "job {token} not created under job control",
        DiagnosticKey.DECLARE_NOT_FOUND: "not found: {name}",
        DiagnosticKey.SET_CANT_ACCESS_TTY: "set: can't access tty; job control turned off",
        DiagnosticKey.UNSET_BAD_VARIABLE_NAME: "-: bad variable name",
        DiagnosticKey.ARITH_DIVIDE_BY_ZERO: "divide by zero",
        DiagnosticKey.ARITH_SYNTAX_ERROR: "arithmetic syntax error",
        DiagnosticKey.PERMISSION_DENIED: ": Permission denied",
        DiagnosticKey.PERMISSION_DENIED_NAME: "{name}: Permission denied",
        DiagnosticKey.FILE_NAME_TOO_LONG_NAME: "{name}: File name too long",
        DiagnosticKey.ERRNO_NAME: "{name}: {error}",
        DiagnosticKey.PY_USAGE: "usage: {entry} [-e] [-x] [--no-dedent] [-v VAR] [-r VAR] [-t VAR] [-u VAR] [CODE]",
        DiagnosticKey.UNALIAS_USAGE: "unalias: usage: unalias [-a] name ...",
        DiagnosticKey.WRITE_ERROR: "ash: write error: {error}",
        DiagnosticKey.FC_USAGE: "usage: fc [-e ename] [-lnr] [first] [last] or fc -s [old=new] [command]",
        DiagnosticKey.FC_NO_HISTORY: "fc: no command found",
        DiagnosticKey.FC_EVENT_NOT_FOUND: "fc: event not found: {ref}",
        DiagnosticKey.FC_INVALID_EDITOR: "fc: invalid editor command",
        DiagnosticKey.FC_RECURSION_GUARD: "fc: recursive replay blocked",
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
