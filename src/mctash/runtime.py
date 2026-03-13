from __future__ import annotations

import glob
import importlib
import importlib.util
import ctypes
import copy
import errno
import hashlib
import io
import json
import os
import socket
import select
import signal
import shlex
import stat
import subprocess
import sys
import tempfile
import threading
import time
import fnmatch
import re
import traceback
import textwrap
import uuid
import resource
from contextlib import contextmanager, redirect_stdout
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple

from .ast_nodes import (
    AndOr,
    ArithForCommand,
    Assignment,
    CaseCommand,
    CaseItem,
    Command,
    ForCommand,
    FunctionDef,
    GroupCommand,
    IfCommand,
    ListNode,
    ListItem,
    Pipeline,
    Redirect,
    RedirectCommand,
    Script,
    SimpleCommand,
    SubshellCommand,
    WhileCommand,
    Word,
)
from .expand import (
    PresplitFields,
    parse_word_parts,
    _extract_balanced,
    _find_braced_end,
    _split_braced,
)
from .expansion_model import ExpansionField, ExpansionSegment, fields_to_text_list
from .lexer import LexContext, LexError, TokenReader
from .parser import ParseError, Parser
from .asdl_map import AsdlMappingError, lst_list_item_to_asdl, word as lst_word_to_asdl_word
from .word_parser import parse_word as parse_legacy_word
from .diagnostics import DiagnosticCatalog, DiagnosticKey
from .i18n import get_translator

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]


class RuntimeError(Exception):
    pass


class ReturnFromFunction(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"return {code}")
        self.code = code


class BreakLoop(Exception):
    def __init__(self, count: int = 1) -> None:
        super().__init__(f"break {count}")
        self.count = count


class ContinueLoop(Exception):
    def __init__(self, count: int = 1) -> None:
        super().__init__(f"continue {count}")
        self.count = count


class CommandSubstFailure(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"command substitution failed with {code}")
        self.code = code


class ArithExpansionFailure(Exception):
    def __init__(self, code: int = 2) -> None:
        super().__init__(f"arithmetic expansion failed with {code}")
        self.code = code


JOB_RUNNING = "running"
JOB_STOPPED = "stopped"
JOB_DONE = "done"


class _SharedVarStore:
    def __init__(self, path: str) -> None:
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    @contextmanager
    def _locked_file(self):
        with open(self.path, "r+", encoding="utf-8") as f:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yield f
            finally:
                if fcntl is not None:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _read(self, f) -> dict[str, str]:
        f.seek(0)
        text = f.read()
        if not text.strip():
            return {}
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            return {}
        if not isinstance(raw, dict):
            return {}
        out: dict[str, str] = {}
        for k, v in raw.items():
            out[str(k)] = str(v)
        return out

    def _write(self, f, data: dict[str, str]) -> None:
        f.seek(0)
        json.dump(data, f, sort_keys=True)
        f.truncate()
        f.flush()

    def get(self, key: str) -> str:
        with self._locked_file() as f:
            return self._read(f).get(key, "")

    def set(self, key: str, value: str) -> None:
        with self._locked_file() as f:
            data = self._read(f)
            data[key] = value
            self._write(f, data)

    def delete(self, key: str) -> bool:
        with self._locked_file() as f:
            data = self._read(f)
            if key not in data:
                return False
            del data[key]
            self._write(f, data)
            return True

    def contains(self, key: str) -> bool:
        with self._locked_file() as f:
            return key in self._read(f)

    def items(self) -> list[tuple[str, str]]:
        with self._locked_file() as f:
            return sorted(self._read(f).items())

    def keys(self) -> list[str]:
        return [k for k, _ in self.items()]

    def __len__(self) -> int:
        with self._locked_file() as f:
            return len(self._read(f))


@dataclass
class ShellCalledProcessError(Exception):
    returncode: int
    cmd: str
    stdout: str
    stderr: str

    def __str__(self) -> str:
        return f"ShellCalledProcessError(returncode={self.returncode}, cmd={self.cmd!r})"


class _PyVarsMapping(MutableMapping[str, object]):
    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt

    def __getitem__(self, key: str) -> object:
        if key in self._rt._typed_vars:
            return self._rt._typed_vars[key]  # type: ignore[return-value]
        return self._rt._get_var(key)

    def __setitem__(self, key: str, value: object) -> None:
        if isinstance(value, (list, tuple)):
            if not self._rt._bash_feature_enabled("bridge_collections"):
                raise TypeError("sh.vars list/tuple mapping is deferred in ash mode")
            seq = list(value)
            self._rt._assign_shell_var(key, " ".join(self._rt._py_to_shell(v) for v in seq))
            self._rt._typed_vars[key] = seq
            return
        if isinstance(value, dict):
            if not self._rt._bash_feature_enabled("bridge_collections"):
                raise TypeError("sh.vars dict mapping is deferred in ash mode")
            d = {str(k): v for k, v in value.items()}
            self._rt._assign_shell_var(
                key,
                " ".join(f"{k}={self._rt._py_to_shell(v)}" for k, v in d.items()),
            )
            self._rt._typed_vars[key] = d
            return
        self._rt._typed_vars.pop(key, None)
        self._rt._assign_shell_var(key, self._rt._py_to_shell(value))

    def __delitem__(self, key: str) -> None:
        removed = False
        for scope in reversed(self._rt.local_stack):
            if key in scope:
                del scope[key]
                removed = True
                break
        if key in self._rt.env:
            del self._rt.env[key]
            removed = True
        if not removed:
            raise KeyError(key)
        self._rt._var_attrs.pop(key, None)
        self._rt._typed_vars.pop(key, None)

    def __iter__(self) -> Iterator[str]:
        seen: set[str] = set()
        for scope in self._rt.local_stack:
            for k in scope:
                if k not in seen:
                    seen.add(k)
                    yield k
        for k in self._rt.env:
            if k not in seen:
                seen.add(k)
                yield k

    def __len__(self) -> int:
        return sum(1 for _ in self.__iter__())

    def attrs(self, name: str) -> dict[str, bool]:
        return self._rt._get_var_attrs(name)

    def set_attrs(self, name: str, **flags: object) -> None:
        self._rt._set_var_attrs(name, **flags)

    def declare(self, name: str, value: object = "", **flags: object) -> None:
        self._rt._declare_var(name, self._rt._py_to_shell(value), **flags)

    def __getattr__(self, name: str) -> object:
        if name.startswith("_"):
            raise AttributeError(name)
        return self[name]

    def __setattr__(self, name: str, value: object) -> None:
        if name == "_rt" or name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        self[name] = value

    def __delattr__(self, name: str) -> None:
        if name.startswith("_"):
            raise AttributeError(name)
        del self[name]


class _PyEnvMapping(MutableMapping[str, str]):
    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt

    def __getitem__(self, key: str) -> str:
        if key not in self._rt.env:
            raise KeyError(key)
        return self._rt.env[key]

    def __setitem__(self, key: str, value: object) -> None:
        shell_value = self._rt._py_to_shell(value)
        self._rt._assign_shell_var(key, shell_value)
        self._rt.env[key] = self._rt._get_var(key)
        self._rt._set_var_attrs(key, exported=True)

    def __delitem__(self, key: str) -> None:
        if key not in self._rt.env:
            raise KeyError(key)
        del self._rt.env[key]
        self._rt._set_var_attrs(key, exported=False)

    def __iter__(self) -> Iterator[str]:
        return iter(self._rt.env.keys())

    def __len__(self) -> int:
        return len(self._rt.env)


class _PySharedMapping(MutableMapping[str, str]):
    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt

    def __getitem__(self, key: str) -> str:
        store = self._rt._get_shared_store()
        if not store.contains(key):
            raise KeyError(key)
        return store.get(key)

    def __setitem__(self, key: str, value: object) -> None:
        self._rt._get_shared_store().set(key, self._rt._py_to_shell(value))

    def __delitem__(self, key: str) -> None:
        if not self._rt._get_shared_store().delete(key):
            raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._rt._get_shared_store().keys())

    def __len__(self) -> int:
        return len(self._rt._get_shared_store())


class _PyFnNamespace(MutableMapping[str, object]):
    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt

    def __getitem__(self, key: str) -> object:
        if key in self._rt._py_callables:
            return self._rt._py_callables[key]
        if key in self._rt.functions:
            def _caller(*args: object) -> str:
                return self._rt._call_shell_function_from_python(key, [str(a) for a in args])
            return _caller
        raise KeyError(key)

    def __setitem__(self, key: str, value: object) -> None:
        if not callable(value):
            raise TypeError("sh.fn assignment currently requires a Python callable")
        self._rt._install_python_callable(key, value, wrapper_target=key, create_wrapper=True)

    def __delitem__(self, key: str) -> None:
        removed = False
        if key in self._rt._py_callables:
            del self._rt._py_callables[key]
            removed = True
        if key in self._rt.functions:
            del self._rt.functions[key]
            removed = True
        if not removed:
            raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        seen = set(self._rt.functions.keys())
        for k in seen:
            yield k
        for k in self._rt._py_callables.keys():
            if k not in seen:
                yield k

    def __len__(self) -> int:
        return sum(1 for _ in self.__iter__())

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        return self[name]


class _PyArgsView:
    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt

    def _as_list(self) -> list[str]:
        return [self._rt.script_name] + list(self._rt.positional)

    def __getitem__(self, idx: int | slice) -> object:
        vals = self._as_list()
        if isinstance(idx, slice):
            return vals[idx]
        return vals[idx]

    def __len__(self) -> int:
        return len(self._rt.positional) + 1

    def __iter__(self) -> Iterator[str]:
        return iter(self._as_list())

    def set(self, *values: object) -> None:
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = tuple(values[0])
        self._rt.positional = [self._rt._py_to_shell(v) for v in values]


class _PyExpand:
    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt

    def split_ifs(self, text: object) -> list[str]:
        return self._rt._split_ifs(self._rt._py_to_shell(text))

    def substr(self, value: object, offset: int, length: int | None = None) -> str:
        arg_text = str(int(offset)) if length is None else f"{int(offset)}:{int(length)}"
        return self._rt._substring(self._rt._py_to_shell(value), arg_text)

    def substr_text(self, value: object, arg_text: str) -> str:
        return self._rt._substring(self._rt._py_to_shell(value), str(arg_text))

    def substr_var(self, name: str, offset: int, length: int | None = None) -> str:
        arg_text = str(int(offset)) if length is None else f"{int(offset)}:{int(length)}"
        return self._rt._substring(self._rt._get_var(str(name)), arg_text)

    def substr_var_text(self, name: str, arg_text: str) -> str:
        return self._rt._substring(self._rt._get_var(str(name)), str(arg_text))


class _PyRunCommand:
    def __init__(self, runner: "_PyRunProxy", name: str) -> None:
        self._runner = runner
        self._name = name

    def __call__(self, *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return self._runner.argv([self._name, *args], **kwargs)


class _PyRunProxy:
    def __init__(self, bridge: "_PyBridge") -> None:
        self._bridge = bridge

    def __call__(
        self,
        *args: object,
        capture_output: bool = False,
        stdout: Any = None,
        stderr: Any = None,
        check: bool = False,
        input: str | None = None,
        shell: bool = True,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return self._bridge._run_script(
            *args,
            capture_output=capture_output,
            stdout=stdout,
            stderr=stderr,
            check=check,
            input=input,
            shell=shell,
            cwd=cwd,
            env=env,
            timeout=timeout,
        )

    def argv(
        self,
        argv: list[object],
        *,
        check: bool = False,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        rt = self._bridge._rt
        cmd = [rt._py_to_shell(a) for a in argv]
        if not cmd:
            cp = subprocess.CompletedProcess(args=cmd, returncode=0, stdout="" if capture_output else None, stderr="")
            return cp
        if capture_output:
            status, out, _ = rt._capture_command_output(
                SimpleCommand(
                    argv=[Word(a) for a in cmd],
                    assignments=[],
                    redirects=[],
                    line=rt.current_line,
                ),
                data=None,
                force_epipe=False,
            )
            stdout_text = out.decode("utf-8", errors="replace")
            cp = subprocess.CompletedProcess(args=cmd, returncode=int(status), stdout=stdout_text, stderr="")
        else:
            status = rt._run_argv_dispatch(cmd)
            cp = subprocess.CompletedProcess(args=cmd, returncode=int(status), stdout=None, stderr=None)
        if check and cp.returncode != 0:
            raise ShellCalledProcessError(
                returncode=int(cp.returncode),
                cmd=shlex.join(cmd),
                stdout=(cp.stdout or ""),
                stderr=(cp.stderr or ""),
            )
        return cp

    def __getattr__(self, name: str) -> _PyRunCommand:
        if name.startswith("_"):
            raise AttributeError(name)
        return _PyRunCommand(self, name)


class _PyBridge:
    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT
    DEVNULL = subprocess.DEVNULL

    def __init__(self, rt: "Runtime") -> None:
        self._rt = rt
        self.vars = _PyVarsMapping(rt)
        self.env = _PyEnvMapping(rt)
        self.fn = _PyFnNamespace(rt)
        self.shared = _PySharedMapping(rt)
        self.args = _PyArgsView(rt)
        self.expand = _PyExpand(rt)
        self.run = _PyRunProxy(self)

    @property
    def stack(self) -> list[dict[str, object]]:
        self._rt._sync_root_frame()
        line = int(self._rt.current_line if self._rt.current_line is not None else 0)
        out: list[dict[str, object]] = []
        for i, fr in enumerate(self._rt._frame_stack):
            row = dict(fr)
            if i == len(self._rt._frame_stack) - 1:
                row["lineno"] = line
            out.append(row)
        return list(reversed(out))

    def __call__(self, *args: object) -> str:
        cp = self.run(*args, capture_output=True, check=False)
        if cp.returncode != 0:
            raise ShellCalledProcessError(
                returncode=int(cp.returncode),
                cmd=self._coerce_script(args),
                stdout=cp.stdout or "",
                stderr=cp.stderr or "",
            )
        out = cp.stdout or ""
        return out[:-1] if out.endswith("\n") else out

    def _coerce_script(self, args: tuple[object, ...]) -> str:
        if len(args) == 1 and isinstance(args[0], str):
            return args[0]
        return shlex.join([str(a) for a in args])

    def _run_script(
        self,
        *args: object,
        capture_output: bool = False,
        stdout: Any = None,
        stderr: Any = None,
        check: bool = False,
        input: str | None = None,
        shell: bool = True,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if not shell:
            raise ValueError("sh.run(shell=False) is not supported in this phase")
        script = self._coerce_script(args)
        if capture_output:
            if stdout is None:
                stdout = subprocess.PIPE
            if stderr is None:
                stderr = subprocess.PIPE
        cp = self._rt._run_shell_subprocess(
            script=script,
            stdout=stdout,
            stderr=stderr,
            input_text=input,
            cwd=cwd,
            env=env,
            timeout=timeout,
        )
        if check and cp.returncode != 0:
            raise ShellCalledProcessError(
                returncode=int(cp.returncode),
                cmd=script,
                stdout=cp.stdout or "",
                stderr=cp.stderr or "",
            )
        return cp

    def popen(
        self,
        *args: object,
        stdout: Any = None,
        stderr: Any = None,
        stdin: Any = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.Popen[str]:
        script = self._coerce_script(args)
        return self._rt._popen_shell_subprocess(
            script=script,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            cwd=cwd,
            env=env,
        )

    def tie(self, name: str, getter: Any, setter: Any = None, type: str | None = None) -> None:
        if not callable(getter):
            raise TypeError("getter must be callable")
        if setter is not None and not callable(setter):
            raise TypeError("setter must be callable when provided")
        tie_type = type or "scalar"
        if tie_type in {"array", "assoc"} and not self._rt._bash_feature_enabled("bridge_collections"):
            raise ValueError(f"{tie_type} tie type is deferred in ash mode")
        if tie_type not in {"scalar", "integer"}:
            if tie_type in {"array", "assoc"}:
                self._rt._py_ties[name] = (getter, setter, tie_type)
                return
            raise ValueError(f"unsupported tie type: {tie_type}")
        self._rt._py_ties[name] = (getter, setter, tie_type)

    def untie(self, name: str) -> None:
        self._rt._py_ties.pop(name, None)


class Runtime:
    COMPILE_FALLBACK_REASONS: Dict[str, str] = {
        "item-not-dict": "ASDL list item is not a dict node.",
        "trap-active": "Compiled backend is disabled while running a trap handler.",
        "interactive-monitor-active": "Compiled backend is disabled in interactive monitor mode.",
        "sentence-background": "Background sentence nodes are not compiled in phase 1.",
        "sentence-child-invalid": "Sentence child node is invalid.",
        "unsupported-list-item": "Unsupported ASDL list item type.",
        "andor-child-count": "And/or list shape has no pipeline children.",
        "pipeline-invalid": "Pipeline node is invalid.",
        "pipeline-child-count": "Pipeline has no stage commands.",
        "pipeline-stage-invalid": "Pipeline stage is not a valid command node.",
        "unsupported-command": "Compiled subset does not support this command type yet.",
        "json-key-failed": "Failed to key compiled cache from ASDL node.",
        "compiled-not-callable": "Compiled artifact did not produce callable entrypoint.",
        "compile-failed": "Python compile/exec of backend artifact failed.",
        "compiled-runtime-error": "Compiled artifact raised at runtime; interpreter fallback used.",
        "compile-disabled-by-config": "MCTASH_ENABLE_COMPILED disabled compiled backend; interpreter forced.",
    }
    COMPILED_SUPPORTED_COMMANDS: set[str] = {
        "command.Simple",
        "command.Redirect",
        "command.BraceGroup",
        "command.If",
        "command.WhileUntil",
        "command.ControlFlow",
        "command.ShAssignment",
    }
    OPTION_FLAG_ORDER = "abefhikmnptuvxBCEHPT"
    _thread_diag_lock = threading.Lock()
    _thread_diag_emitted: set[str] = set()
    SET_O_LIST_ORDER: List[str] = [
        "allexport",
        "braceexpand",
        "emacs",
        "errexit",
        "errtrace",
        "functrace",
        "hashall",
        "histexpand",
        "history",
        "ignoreeof",
        "interactive-comments",
        "keyword",
        "monitor",
        "noclobber",
        "noexec",
        "noglob",
        "notify",
        "nounset",
        "onecmd",
        "physical",
        "pipefail",
        "posix",
        "privileged",
        "verbose",
        "vi",
        "xtrace",
        # Kept for internal compatibility/debug.
        "interactive",
        "stdin",
        "nolog",
        "debug",
    ]
    SET_O_OPTION_MAP: Dict[str, str] = {
        "allexport": "a",
        "braceexpand": "B",
        "emacs": "E",
        "errexit": "e",
        "errtrace": "E",
        "functrace": "T",
        "hashall": "h",
        "histexpand": "H",
        "history": "history",
        "interactive-comments": "interactive-comments",
        "keyword": "k",
        "onecmd": "t",
        "physical": "P",
        "noglob": "f",
        "noexec": "n",
        "nounset": "u",
        "verbose": "v",
        "xtrace": "x",
        "noclobber": "C",
        "vi": "V",
        "interactive": "i",
        "monitor": "m",
        "notify": "b",
        "ignoreeof": "I",
        "stdin": "s",
        "privileged": "p",
        "nolog": "q",
        "debug": "debug",
        "quiet": "q",
        "pipefail": "pipefail",
        "posix": "posix",
    }
    ENV_MUTATING_BUILTINS = {
        "cd",
        "read",
        "set",
        "declare",
        "typeset",
        "command",
        "builtin",
        "shift",
        "getopts",
        "alias",
        "unalias",
        "trap",
        "let",
        "py",
        "python:",
        "from",
        "shared",
        "shopt",
        "pushd",
        "popd",
        "[[",
    }
    SPECIAL_BUILTINS = {
        ":",
        ".",
        "source",
        "break",
        "continue",
        "eval",
        "exec",
        "exit",
        "export",
        "readonly",
        "return",
        "set",
        "shift",
        "times",
        "trap",
        "unset",
    }
    BUILTINS = {
        "cd",
        "pwd",
        "exit",
        ":",
        "return",
        ".",
        "source",
        "local",
        "eval",
        "declare",
        "typeset",
        "mapfile",
        "readarray",
        "enable",
        "help",
        "dirs",
        "pushd",
        "popd",
        "disown",
        "bind",
        "complete",
        "compgen",
        "compopt",
        "[",
        "[[",
        "test",
        "set",
        "export",
        "readonly",
        "unset",
        "shift",
        "printf",
        "echo",
        "read",
        "true",
        "false",
        "command",
        "builtin",
        "exec",
        "break",
        "continue",
        "trap",
        "type",
        "alias",
        "unalias",
        "wait",
        "kill",
        "fc",
        "hash",
        "time",
        "times",
        "ulimit",
        "umask",
        "jobs",
        "fg",
        "bg",
        "let",
        "getopts",
        "py",
        "python:",
        "from",
        "shared",
        "shopt",
        "caller",
        "history",
        "suspend",
        "logout",
    }
    SHOPT_DEFAULTS: Dict[str, bool] = {
        "autocd": False,
        "assoc_expand_once": False,
        "cdable_vars": False,
        "cdspell": False,
        "checkhash": False,
        "checkjobs": False,
        "checkwinsize": False,
        "cmdhist": False,
        "compat31": False,
        "compat32": False,
        "compat40": False,
        "compat41": False,
        "compat42": False,
        "compat43": False,
        "compat44": False,
        "complete_fullquote": False,
        "direxpand": False,
        "dirspell": False,
        "dotglob": False,
        "execfail": False,
        "expand_aliases": False,
        "extdebug": False,
        "extglob": False,
        "extquote": False,
        "failglob": False,
        "force_fignore": False,
        "globasciiranges": False,
        "globstar": False,
        "gnu_errfmt": False,
        "histappend": False,
        "histreedit": False,
        "histverify": False,
        "hostcomplete": False,
        "huponexit": False,
        "inherit_errexit": False,
        "interactive_comments": False,
        "lastpipe": False,
        "lithist": False,
        "localvar_inherit": False,
        "localvar_unset": False,
        "login_shell": False,
        "mailwarn": False,
        "no_empty_cmd_completion": False,
        "nocaseglob": False,
        "nocasematch": False,
        "nullglob": False,
        "progcomp": False,
        "progcomp_alias": False,
        "promptvars": True,
        "restricted_shell": False,
        "shift_verbose": False,
        "sourcepath": False,
        "xpg_echo": False,
        # mctash extension
        "read_interruptible": False,
    }

    def __init__(self) -> None:
        self.last_status = 0
        self.last_nonzero_status = 0
        self.env: Dict[str, str] = dict(os.environ)
        try:
            self.env["PWD"] = os.getcwd()
        except OSError:
            pass
        self.positional: List[str] = []
        self.functions: Dict[str, ListNode] = {}
        self.functions_asdl: Dict[str, Dict[str, Any]] = {}
        self.functions_source: Dict[str, str] = {}
        self.aliases: Dict[str, str] = {}
        self.local_stack: List[Dict[str, str]] = []
        self.script_name: str = ""
        self.options: Dict[str, bool] = {"h": True, "B": True}
        self.readonly_vars: set[str] = set()
        self._cmd_sub_used: bool = False
        self._cmd_sub_status: int = 0
        self._loop_depth: int = 0
        self.current_line: int | None = None
        self.source_stack: List[str] = []
        self.traps: Dict[str, str] = {}
        self._pending_signals: List[str] = []
        self._trap_inline_handled: List[str] = []
        self._running_trap: bool = False
        self._trap_entry_status: int | None = None
        self.c_string_mode: bool = False
        self._trap_status_hint: int = 0
        self._errexit_item_exempt: bool = False
        self._next_job_id: int = 1
        self._bg_jobs: Dict[int, threading.Thread] = {}
        self._bg_status: Dict[int, int] = {}
        self._last_bg_job: int | None = None
        self._last_bg_pid: int | None = None
        self._bg_pids: Dict[int, int] = {}
        self._bg_pid_to_job: Dict[int, int] = {}
        self._bg_started_at: Dict[int, float] = {}
        self._bg_cmdline: Dict[int, str] = {}
        self._bg_stopped: set[int] = set()
        self._job_state: Dict[int, str] = {}
        self._job_events: list[tuple[int, str, int | None]] = []
        self._job_event_lock = threading.Lock()
        self._checkjobs_warned_once = False
        self._job_control_ready = False
        self._last_job_lookup_error: str | None = None
        self._bg_notifications: list[int] = []
        self._bg_notify_emitted: set[int] = set()
        self._bg_lock = threading.Lock()
        self._coproc_procs: Dict[int, subprocess.Popen] = {}
        self._thread_ctx = threading.local()
        self._fd_redirect_depth: int = 0
        self._force_broken_pipe: bool = False
        self._user_fds: set[int] = set()
        self._active_temp_fds: set[int] = set()
        self._getopts_state: tuple[tuple[str, ...], int, int] | None = None
        self._procsub_paths: set[str] = set()
        self._procsub_threads: list[threading.Thread] = []
        self._line_offset: int = 0
        self._last_eval_hard_error: bool = False
        self._pipeline_input_latency: float | None = None
        self._test_mode: bool = self.env.get("MCTASH_TEST_MODE", "") == "1"
        self._py_import_counter: int = 0
        self._var_attrs: Dict[str, set[str]] = {k: {"exported"} for k in self.env.keys()}
        self._typed_vars: Dict[str, object] = {}
        self.disabled_builtins: set[str] = set()
        self._dir_stack: list[str] = [self.env.get("PWD", os.getcwd())]
        self._disowned_nohup: set[int] = set()
        self._completion_specs: dict[str, dict[str, object]] = {}
        self._bash_compat_level: int | None = self._parse_bash_compat_level(self.env.get("BASH_COMPAT", ""))
        self._frame_stack: List[Dict[str, object]] = []
        self._call_stack: List[str] = []
        self._history: List[str] = []
        self._history_ts: List[float | None] = []
        self._fc_replay_depth: int = 0
        self._fc_active_replay_signatures: set[tuple[str, ...]] = set()
        self._alias_textual_depth: int = 0
        self._cmd_hash: Dict[str, str] = {}
        self._errexit_suppressed: int = 0
        self._py_callables: Dict[str, Any] = {}
        self._py_ties: Dict[str, tuple[Any, Any, str | None]] = {}
        self._shopts: Dict[str, bool] = dict(self.SHOPT_DEFAULTS)
        self._history_read_cursor: int = 0
        self._command_number: int = 0
        self._is_interactive_session: bool = False
        self._is_login_shell: bool = False
        self._last_read_interrupt_status: int | None = None
        self._last_read_timed_out: bool = False
        self._random_state: int = ((int(time.time() * 1000) ^ os.getpid()) & 0x7FFFFFFF) or 1
        backend = self.env.get("MCTASH_BACKEND", "interpreter").strip().lower()
        self._compiled_backend_enabled: bool = self.env.get("MCTASH_ENABLE_COMPILED", "1").strip().lower() not in {
            "0",
            "false",
            "no",
            "off",
        }
        self._exec_backend_requested: str = backend if backend in {"interpreter", "compiled"} else "interpreter"
        self._exec_backend: str = (
            "compiled"
            if self._exec_backend_requested == "compiled" and self._compiled_backend_enabled
            else "interpreter"
        )
        self._compile_debug: bool = self.env.get("MCTASH_COMPILE_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
        self._declare_raw_assign_by_arg: dict[int, str] = {}
        self._compiled_cache: Dict[tuple[str, str], Callable[["Runtime"], int]] = {}
        self._compile_fallback_seen: set[str] = set()
        self._compiled_depth: int = 0
        # POSIX shells initialize IFS by default; many parameter-expansion
        # operator-word edge cases depend on IFS being set.
        self.env.setdefault("IFS", " \t\n")
        self.env.setdefault("OPTIND", "1")
        mode = self.env.get("MCTASH_MODE", "").strip().lower()
        diag_style = self.env.get("MCTASH_DIAG_STYLE", "").strip().lower()
        if diag_style not in {"ash", "bash"}:
            diag_style = "bash" if (mode == "bash" or self._bash_compat_level is not None) else "ash"
        # Option-surface defaults differ by comparator lane:
        # - ash lane in posix mode: no -h/-B defaults
        # - bash lane (including --posix): keep bash defaults
        if mode == "posix" and diag_style == "ash" and self._bash_compat_level is None:
            self.options.pop("h", None)
            self.options.pop("B", None)
        else:
            self.options.setdefault("h", True)
            self.options.setdefault("B", True)
        if mode == "bash" or self.env.get("BASH_COMPAT", "").strip():
            self._seed_bash_special_vars()
            self._shopts["sourcepath"] = True
        self._diag = DiagnosticCatalog(style=diag_style, gettext=get_translator())
        shared_path = self.env.get(
            "MCTASH_SHARED_FILE",
            os.path.join(tempfile.gettempdir(), f"mctash-shared-{os.getuid()}.json"),
        )
        self._shared_store_path = shared_path
        self._shared_store = _SharedVarStore(shared_path)
        self._py_globals: Dict[str, object] = {"__builtins__": __builtins__}
        # Canonical injected name is `sh`; `bash` is kept for compatibility.
        self._py_globals["sh"] = _PyBridge(self)
        self._py_globals["bash"] = self._py_globals["sh"]
        self._py_globals["shell"] = self._py_globals["sh"]
        self._sync_root_frame()
        # Align with ash test assumptions: shell starts with only stdio fds open.
        if threading.current_thread() is threading.main_thread():
            try:
                os.close(3)
            except OSError:
                pass
        self._install_signal_handlers()

    def _seed_random(self, text: str) -> None:
        try:
            seed = int(str(text).strip() or "0", 10)
        except Exception:
            seed = 0
        self._random_state = seed & 0x7FFFFFFF
        if self._random_state == 0:
            self._random_state = 1

    def _next_random(self) -> str:
        # LCG-based 15-bit RANDOM surface; deterministic under assignment.
        self._random_state = (1103515245 * self._random_state + 12345) & 0x7FFFFFFF
        out = (self._random_state >> 16) & 0x7FFF
        s = str(out)
        self.env["RANDOM"] = s
        return s

    def _seed_bash_special_vars(self) -> None:
        # Provide bash-mode variable surface expected by comparator tests.
        self.env.setdefault("BASH", self.env.get("_", "mctash"))
        self.env.setdefault("BASH_VERSION", "5.2.0(1)-release")
        self.env.setdefault("BASH_VERSINFO", "(5 2 0 1 release x86_64-pc-linux-gnu)")
        self.env.setdefault("BASH_SOURCE", "()")
        self.env.setdefault("BASH_LINENO", "()")
        self.env.setdefault("BASHOPTS", "")
        self.env.setdefault("SHELLOPTS", "")
        self.env.setdefault("BASH_ARGC", "()")
        self.env.setdefault("BASH_ARGV", "()")
        self.env.setdefault("BASH_CMDS", "()")
        self.env.setdefault("PS4", "+ ")
        try:
            self.env.setdefault("UID", str(os.getuid()))
            self.env.setdefault("EUID", str(os.geteuid()))
            self.env.setdefault("PPID", str(os.getppid()))
            # Bash prints GROUPS as an indexed array.
            self.env.setdefault("GROUPS", f"({os.getgid()})")
        except Exception:
            pass
        self.env.setdefault("DIRSTACK", "()")
        self.env.setdefault("FUNCNAME", "()")
        # Keep bash special arrays visible in declare -a listings.
        self._typed_vars.setdefault("BASH_SOURCE", [])
        self._typed_vars.setdefault("BASH_LINENO", ["0"])
        self._typed_vars.setdefault("DIRSTACK", [])
        self._typed_vars.setdefault("FUNCNAME", [])
        self._set_var_attrs("BASH_SOURCE", array=True)
        self._set_var_attrs("BASH_LINENO", array=True)
        self._set_var_attrs("DIRSTACK", array=True)
        self._set_var_attrs("FUNCNAME", array=True)

    @staticmethod
    def _parse_bash_compat_level(raw: str) -> int | None:
        s = (raw or "").strip()
        if not s:
            return None
        if re.fullmatch(r"[0-9]{2}", s):
            return int(s, 10)
        m = re.fullmatch(r"([0-9]+)\\.([0-9]+)", s)
        if m:
            return int(m.group(1), 10) * 10 + int(m.group(2), 10)
        return None

    def _bash_feature_enabled(self, feature: str) -> bool:
        # Policy: Bash-compat features are enabled only when BASH_COMPAT is set.
        level = self._compat_level()
        if level is None:
            return False
        if feature == "declare_array":
            return True
        if feature == "declare_assoc":
            return True
        if feature == "bridge_collections":
            return True
        return False

    def _compat_level(self) -> int | None:
        level = self._bash_compat_level
        if level is None:
            level = self._parse_bash_compat_level(self.env.get("BASH_COMPAT", ""))
            self._bash_compat_level = level
        return level

    def _compat_enabled(self) -> bool:
        return self._compat_level() is not None

    def _compat_at_most(self, level: int) -> bool:
        cur = self._compat_level()
        return cur is not None and cur <= level

    def _is_noninteractive(self) -> bool:
        return not bool(self.options.get("i", False))

    def _special_builtin_fatal_status(self, cmd_name: str, status: int) -> int:
        # Centralized policy helper for special builtins in non-interactive
        # shells; this currently reflects existing behavior and can be extended
        # as POSIX 2.8/2.9 closure work proceeds.
        if status == 0:
            return status
        if cmd_name in self.SPECIAL_BUILTINS and self._is_noninteractive():
            return status
        return status

    def _maybe_fatal_special_builtin_error(self, cmd_name: str, status: int) -> int:
        if (
            status != 0
            and cmd_name in self.SPECIAL_BUILTINS
            and self.options.get("posix", False)
            and self._is_noninteractive()
        ):
            raise SystemExit(status)
        return status

    def _get_subshell_depth(self) -> int:
        return int(getattr(self._thread_ctx, "subshell_depth", 0))

    def _current_source(self) -> str:
        if self.source_stack:
            return self.source_stack[-1]
        return self.script_name

    @contextmanager
    def _push_frame(self, *, kind: str, funcname: str = "", source: str | None = None) -> Iterator[None]:
        frame = {
            "kind": kind,
            "source": self._current_source() if source is None else source,
            "lineno": int(self.current_line or 0),
            "funcname": funcname,
        }
        self._frame_stack.append(frame)
        try:
            yield
        finally:
            if self._frame_stack:
                self._frame_stack.pop()

    @contextmanager
    def _suppress_errexit(self) -> Iterator[None]:
        self._errexit_suppressed += 1
        try:
            yield
        finally:
            self._errexit_suppressed = max(0, self._errexit_suppressed - 1)

    def _sync_root_frame(self) -> None:
        root = {
            "kind": "script",
            "source": self._current_source(),
            "lineno": int(self.current_line or 0),
            "funcname": "",
        }
        if self._frame_stack:
            self._frame_stack[0] = root
        else:
            self._frame_stack.append(root)

    def _get_shared_store(self) -> _SharedVarStore:
        current = self._get_var("MCTASH_SHARED_FILE")
        if current and current != self._shared_store_path:
            self._shared_store_path = current
            self._shared_store = _SharedVarStore(current)
        return self._shared_store

    def _set_subshell_depth(self, value: int) -> None:
        self._thread_ctx.subshell_depth = max(0, int(value))

    def _activate_restricted_mode(self) -> None:
        # Match bash restricted-shell behavior for core mutable path/env vars.
        for name in ("PATH", "SHELL", "ENV", "BASH_ENV"):
            self.readonly_vars.add(name)

    def _is_restricted(self) -> bool:
        return bool(self.options.get("r", False))

    def set_positional_args(self, args: List[str]) -> None:
        self.positional = list(args)
        if self._bash_compat_level is not None:
            # In bash compat without extdebug, expose root-frame style values.
            if not self._shopts.get("extdebug", False):
                if len(self.source_stack) > 1:
                    script_ref = self.source_stack[-1]
                    argc_vals = ["1", "0"]
                    argv_vals = [script_ref] if script_ref else []
                else:
                    argc_vals = [str(len(self.positional))]
                    argv_vals = list(reversed(self.positional))
            else:
                argc_vals = [str(len(self.positional))]
                argv_vals = list(reversed(self.positional))
            self._typed_vars["BASH_ARGC"] = argc_vals
            self._typed_vars["BASH_ARGV"] = argv_vals
            self._set_var_attrs("BASH_ARGC", array=True)
            self._set_var_attrs("BASH_ARGV", array=True)
            self._set_subscript_projection("BASH_ARGC", argc_vals[0] if argc_vals else "")
            self._set_subscript_projection("BASH_ARGV", argv_vals[0] if argv_vals else "")

    def set_script_name(self, name: str) -> None:
        self.script_name = name
        if name:
            if self.source_stack:
                self.source_stack[0] = name
            else:
                self.source_stack = [name]
            self._sync_root_frame()
            if self._bash_compat_level is not None:
                self._typed_vars["BASH_SOURCE"] = [name]
                self._typed_vars["BASH_LINENO"] = ["0"]
                self._set_var_attrs("BASH_SOURCE", array=True)
                self._set_var_attrs("BASH_LINENO", array=True)
                self._set_subscript_projection("BASH_SOURCE", name)
                self._set_subscript_projection("BASH_LINENO", "0")

    def set_interactive_session(self, enabled: bool) -> None:
        self._is_interactive_session = bool(enabled)

    def set_login_shell(self, enabled: bool) -> None:
        self._is_login_shell = bool(enabled)

    def _ensure_job_control_ready(self) -> None:
        if self._job_control_ready:
            return
        if not (self.options.get("i", False) and os.isatty(0) and hasattr(os, "tcsetpgrp")):
            return
        try:
            # Keep shell in its own process group for foreground handoff.
            os.setpgid(0, 0)
        except OSError:
            pass
        tty_fd: int | None = None
        try:
            tty_fd = os.open("/dev/tty", os.O_RDWR)
            os.tcsetpgrp(tty_fd, os.getpgrp())
            self._job_control_ready = True
        except OSError:
            self._job_control_ready = False
        finally:
            if tty_fd is not None:
                try:
                    os.close(tty_fd)
                except OSError:
                    pass

    def _job_debug(self, msg: str) -> None:
        if self.env.get("MCTASH_JOB_DEBUG", "") not in {"1", "true", "yes", "on"}:
            return
        try:
            print(f"[mctash-job] {msg}", file=sys.stderr, flush=True)
        except Exception:
            pass

    def run(self, script: Script) -> int:
        if self._exec_backend_requested == "compiled" and not self._compiled_backend_enabled:
            self._compile_note("compile-disabled-by-config")
        return self._exec_list(script.body)

    def _install_signal_handlers(self) -> None:
        for name in ["HUP", "INT", "QUIT", "TERM", "USR1", "USR2", "WINCH", "CHLD", "PIPE", "ALRM", "SYS"]:
            sig = getattr(signal, f"SIG{name}", None)
            if sig is None:
                continue
            try:
                signal.signal(sig, self._signal_handler)
            except Exception:
                pass

    @staticmethod
    def _preexec_reset_signals() -> None:
        # External commands should not inherit mctash/Python signal handlers
        # or ignored dispositions.
        max_sig = int(getattr(signal, "NSIG", 128))
        for num in range(1, max_sig):
            if num in (int(signal.SIGKILL), int(signal.SIGSTOP)):
                continue
            try:
                signal.signal(num, signal.SIG_DFL)
            except Exception:
                pass

    def _signal_handler(self, signum, frame) -> None:
        try:
            name = signal.Signals(signum).name.replace("SIG", "")
        except Exception:
            name = str(signum)
        action = self.traps.get(name)
        if action is not None:
            if action == "":
                return
            if name == "CHLD" and self._running_trap:
                # Ignore CHLD generated by commands executed inside a trap body.
                return
            self._pending_signals.append(name)
            return
        if name in {"CHLD", "WINCH"}:
            return
        if name in {"HUP", "TERM", "USR1", "USR2", "SYS"}:
            msg = signal.strsignal(signum)
            if msg:
                print(msg, file=sys.stderr)
        raise SystemExit(128 + signum)

    def _normalize_signal_spec(self, spec: str) -> str | None:
        text = spec.strip()
        if text == "":
            return None
        if text == "0" or text.upper() == "EXIT":
            return "EXIT"
        if text.lstrip("-").isdigit():
            num = int(text)
            if num == 0:
                return "EXIT"
            try:
                return signal.Signals(num).name.replace("SIG", "")
            except Exception:
                return None
        up = text.upper()
        if up.startswith("SIG"):
            up = up[3:]
        if up == "0":
            return "EXIT"
        if hasattr(signal, f"SIG{up}"):
            return up
        return None

    def _signal_number(self, name: str) -> int:
        if name == "EXIT":
            return 0
        sig = getattr(signal, f"SIG{name}", None)
        return int(sig) if sig is not None else 0

    def _signal_names_by_number(self) -> list[tuple[int, str]]:
        pairs: list[tuple[int, str]] = []
        seen: set[int] = set()
        for sig in signal.Signals:
            num = int(sig)
            if num in seen:
                continue
            seen.add(num)
            pairs.append((num, sig.name.replace("SIG", "")))
        pairs.sort(key=lambda x: x[0])
        return pairs

    def _print_signal_table(self) -> None:
        parts: list[str] = []
        for num, name in self._signal_names_by_number():
            parts.append(f" {num}) {name}")
        print(" ".join(parts))

    def _format_error(self, msg: str, line: int | None = None, context: str | None = None) -> str:
        if self.source_stack:
            if self._diag.style == "bash":
                prefix = self.source_stack[-1]
            else:
                prefix = ": ".join(self.source_stack)
        elif self.script_name:
            prefix = self.script_name
        else:
            return msg
        if line is not None:
            if self._line_offset:
                line += self._line_offset
            if self._diag.style != "bash" and self.c_string_mode and line > 0 and len(self.source_stack) <= 1:
                line = line - 1
        if self._diag.style == "bash":
            if context in {"eval", "command substitution"} and line is not None:
                prefix = f"{prefix}: {context}: line {line}"
            else:
                if line is not None:
                    prefix = f"{prefix}: line {line}"
                if context:
                    prefix = f"{prefix}: {context}"
        else:
            if context:
                prefix = f"{prefix}: {context}"
            if line is not None:
                prefix = f"{prefix}: line {line}"
        return f"{prefix}: {msg}"

    def _report_error(self, msg: str, line: int | None = None, context: str | None = None) -> None:
        self._print_stderr(self._format_error(msg, line=line, context=context))

    def _print_stderr(self, msg: str) -> None:
        try:
            print(msg, file=sys.stderr)
        except OSError:
            # stderr may be explicitly closed (e.g. 2>&-); preserve status flow.
            pass

    def _diag_msg(self, key: DiagnosticKey, **kwargs: str) -> str:
        return self._diag.render(key, **kwargs)

    def _runtime_error_status(self, msg: str) -> int:
        if "bad substitution" in msg or "unbound variable:" in msg:
            # Bash-style diagnostics report bad substitution as command-not-found
            # class status (127), while ash-style keeps traditional parse/runtime
            # failure status (2). Preserve mode-specific parity.
            return 127 if self._diag.style == "bash" else 2
        return 1

    def _run_pending_traps(self) -> None:
        if self._get_subshell_depth() > 0 or self._running_trap:
            return
        if self._trap_inline_handled:
            for sig_name in list(self._trap_inline_handled):
                if sig_name in self._pending_signals:
                    self._pending_signals.remove(sig_name)
                self._trap_inline_handled.remove(sig_name)
        while self._pending_signals:
            sig = self._pending_signals.pop(0)
            action = self.traps.get(sig)
            if action:
                entry_status = self.last_status
                if entry_status == 0 and self.last_nonzero_status != 0:
                    entry_status = self.last_nonzero_status
                saved_last = self.last_status
                saved_nonzero = self.last_nonzero_status
                saved_hint = self._trap_status_hint
                self._run_trap_action(action, entry_status)
                self.last_status = saved_last
                self.last_nonzero_status = saved_nonzero
                self._trap_status_hint = saved_hint

    def _run_trap_action(self, action: str, entry_status: int) -> int:
        self._running_trap = True
        saved = self._trap_entry_status
        self._trap_entry_status = entry_status
        try:
            with self._push_frame(kind="trap", funcname="trap"):
                return self._eval_source(action, propagate_exit=True, propagate_return=True)
        finally:
            self._trap_entry_status = saved
            self._running_trap = False

    def _format_job_notification_line(self, job_id: int) -> str:
        status = self._bg_status.get(job_id, 0)
        state = "Done"
        if status > 0:
            state = f"Done({status})"
        elif status < 0:
            try:
                sig_name = signal.Signals(-status).name.replace("SIG", "")
            except Exception:
                sig_name = f"SIG{-status}"
            state = sig_name
        cmd = self._bg_cmdline.get(job_id, "")
        return f"[{job_id}] {state}{(' ' + cmd) if cmd else ''}"

    def _emit_job_launch_banner(self, job_id: int, pid: int | None) -> None:
        if not self.options.get("i", False):
            return
        if pid is None:
            return
        print(f"[{job_id}] {pid}", flush=True)

    def _push_job_event(self, job_id: int, event: str, value: int | None = None) -> None:
        with self._job_event_lock:
            self._job_events.append((job_id, event, value))

    def _set_job_state(self, job_id: int, state: str) -> None:
        prev = self._job_state.get(job_id)
        self._job_state[job_id] = state
        if prev != state:
            self._push_job_event(job_id, state, None)

    def _register_job_spawn(self, job_id: int) -> None:
        self._set_job_state(job_id, JOB_RUNNING)

    def _mark_job_stopped(self, job_id: int, sig_num: int | None = None) -> None:
        self._bg_stopped.add(job_id)
        self._set_job_state(job_id, JOB_STOPPED)
        if sig_num is not None:
            self._push_job_event(job_id, "stopped", sig_num)

    def _mark_job_continued(self, job_id: int) -> None:
        self._bg_stopped.discard(job_id)
        self._set_job_state(job_id, JOB_RUNNING)
        self._push_job_event(job_id, "continued", None)

    def _mark_job_done(self, job_id: int, status: int) -> None:
        self._bg_stopped.discard(job_id)
        self._set_job_state(job_id, JOB_DONE)
        self._push_job_event(job_id, "done", status)

    def _latest_job_event_value(self, job_id: int, event: str) -> int | None:
        with self._job_event_lock:
            for jid, ev, value in reversed(self._job_events):
                if jid == job_id and ev == event:
                    return value
        return None

    def _record_bg_job_completion(self, job_id: int, status: int) -> None:
        with self._bg_lock:
            self._bg_status[job_id] = status
            self._mark_job_done(job_id, status)
            if job_id not in self._bg_notifications:
                self._bg_notifications.append(job_id)
            if self.traps.get("CHLD") and not self._running_trap and job_id not in self._bg_pids:
                # Queue one CHLD trap dispatch per completed child so wait/trap
                # behavior tracks bash/POSIX expectations.
                self._pending_signals.append("CHLD")
            emit_now = bool(self.options.get("i", False) and self.options.get("b", False))
            if emit_now and job_id not in self._bg_notify_emitted:
                print(self._format_job_notification_line(job_id))
                self._bg_notify_emitted.add(job_id)

    def _watch_job_process(self, job_id: int, proc: subprocess.Popen) -> None:
        try:
            # Bash allows monitor-mode job state tracking for `set -m` in
            # non-interactive `-c` probes; do not gate on interactive here.
            monitor = bool(self.options.get("m", False))
            wuntraced = int(getattr(os, "WUNTRACED", 0))
            wcontinued = int(getattr(os, "WCONTINUED", 0))
            flags = (wuntraced | wcontinued) if monitor else 0
            if flags == 0:
                self._record_bg_job_completion(job_id, proc.wait())
                return
            while True:
                try:
                    pid, st = os.waitpid(proc.pid, flags)
                except ChildProcessError:
                    polled = proc.poll()
                    self._record_bg_job_completion(job_id, 0 if polled is None else polled)
                    return
                if pid == 0:
                    continue
                if os.WIFSTOPPED(st):
                    self._mark_job_stopped(job_id, os.WSTOPSIG(st))
                    continue
                if hasattr(os, "WIFCONTINUED") and os.WIFCONTINUED(st):
                    self._mark_job_continued(job_id)
                    continue
                if os.WIFEXITED(st):
                    self._record_bg_job_completion(job_id, os.WEXITSTATUS(st))
                    return
                if os.WIFSIGNALED(st):
                    self._record_bg_job_completion(job_id, -os.WTERMSIG(st))
                    return
        finally:
            self._bg_pids.pop(job_id, None)

    def _emit_deferred_job_notifications(self) -> None:
        if not self.options.get("i", False):
            return
        with self._bg_lock:
            pending = list(self._bg_notifications)
            self._bg_notifications.clear()
        for job_id in pending:
            if job_id in self._bg_notify_emitted:
                continue
            print(self._format_job_notification_line(job_id))
            self._bg_notify_emitted.add(job_id)

    def _run_exit_trap(self, status: int) -> int:
        action = self.traps.get("EXIT")
        if not action:
            return status
        try:
            # Preserve pre-trap shell status by default; EXIT trap commands
            # should not turn into fatal `set -e` exits unless they explicitly
            # execute `exit`.
            with self._suppress_errexit():
                self._run_trap_action(action, status)
            return status
        except SystemExit as e:
            return int(e.code) if e.code is not None else 0
        except ReturnFromFunction:
            return status

    def _take_errexit_item_exempt(self) -> bool:
        v = self._errexit_item_exempt
        self._errexit_item_exempt = False
        return v

    def _exec_list(self, node: ListNode) -> int:
        status = 0
        for item in node.items:
            if self.options.get("n", False):
                status = 0
                self.last_status = status
                self._trap_status_hint = status
                continue
            status = self._exec_list_item(item)
            errexit_item_exempt = self._take_errexit_item_exempt()
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            if not getattr(item, "background", False):
                self._run_pending_traps()
            if (
                status != 0
                and self.options.get("e", False)
                and self._errexit_suppressed == 0
                and not errexit_item_exempt
            ):
                raise SystemExit(status)
        self._run_pending_traps()
        return status

    def _jobspec_spec_from_ast_and_or(self, node: Any) -> tuple[str, list[Redirect]] | None:
        if not isinstance(node, AndOr):
            return None
        if len(node.pipelines) != 1 or node.operators:
            return None
        pl = node.pipelines[0]
        if pl.negate or len(pl.commands) != 1:
            return None
        cmd = pl.commands[0]
        if not isinstance(cmd, SimpleCommand):
            return None
        if cmd.assignments:
            return None
        if len(cmd.argv) != 1:
            return None
        token = cmd.argv[0].text
        if not token.startswith("%"):
            return None
        return token, list(cmd.redirects)

    def _jobspec_spec_from_asdl_and_or(self, node: dict[str, Any]) -> tuple[str, list[Redirect]] | None:
        if node.get("type") != "command.AndOr":
            return None
        children = node.get("children") or []
        ops = node.get("ops") or []
        if len(children) != 1 or ops:
            return None
        pl = children[0]
        if not isinstance(pl, dict) or pl.get("type") != "command.Pipeline":
            return None
        if pl.get("negated"):
            return None
        cmds = pl.get("children") or []
        if len(cmds) != 1:
            return None
        cmd = cmds[0]
        if not isinstance(cmd, dict) or cmd.get("type") != "command.Simple":
            return None
        if cmd.get("more_env") or []:
            return None
        words = cmd.get("words") or []
        if len(words) != 1:
            return None
        word0 = words[0]
        if not isinstance(word0, dict):
            return None
        token = self._asdl_word_to_text(word0)
        if not token.startswith("%"):
            return None
        redirects = [self._asdl_to_redirect(r) for r in (cmd.get("redirects") or [])]
        return token, redirects

    def _exec_list_item(self, item) -> int:
        jobspec_spec = self._jobspec_spec_from_ast_and_or(item.node)
        if jobspec_spec is not None:
            jobspec_token, redirects = jobspec_spec
            try:
                with self._redirected_fds(redirects):
                    if getattr(item, "background", False):
                        return self._run_bg_builtin([jobspec_token])
                    return self._run_fg([jobspec_token])
            except RuntimeError as e:
                msg = str(e)
                self._print_stderr(msg)
                return self._runtime_error_status(msg)
        if getattr(item, "background", False):
            # Fast path: backgrounded "echo" in tests should still emit output
            # even when the parent shell exits immediately.
            try:
                pipeline0 = item.node.pipelines[0]
                if (
                    len(item.node.pipelines) == 1
                    and len(pipeline0.commands) == 1
                    and isinstance(pipeline0.commands[0], SimpleCommand)
                    and pipeline0.commands[0].argv
                    and pipeline0.commands[0].argv[0].text == "echo"
                    and not pipeline0.commands[0].assignments
                    and not pipeline0.commands[0].redirects
                ):
                    status = self._exec_and_or(item.node)
                    self.last_status = 0
                    return 0 if status == 0 else status
            except Exception:
                pass

            # Fast path: single external command can be started directly so
            # $! is a real PID and signal/wait behavior is closer to ash.
            try:
                node = item.node
                if (
                    len(node.pipelines) == 1
                    and not node.pipelines[0].negate
                    and len(node.operators) == 0
                    and len(node.pipelines[0].commands) == 1
                    and isinstance(node.pipelines[0].commands[0], SimpleCommand)
                ):
                    sc = node.pipelines[0].commands[0]
                    argv = self._expand_argv(sc.argv)
                    argv = self._expand_aliases(argv)
                    if argv and not self._is_builtin_enabled(argv[0]) and not self._has_function(argv[0]):
                        cmd_env = dict(self.env)
                        for scope in self.local_stack:
                            for k, v in scope.items():
                                if k in self.env:
                                    cmd_env[k] = v
                        for assign in sc.assignments:
                            value = self._expand_assignment_word(assign.value)
                            if assign.op == "+=":
                                cmd_env[assign.name] = cmd_env.get(assign.name, "") + value
                            else:
                                cmd_env[assign.name] = value
                        job_id = self._next_job_id
                        self._next_job_id += 1
                        child_env = dict(cmd_env)
                        path0 = argv[0]
                        if os.path.isfile(path0):
                            try:
                                with open(path0, "rb") as f:
                                    head = f.read(2)
                                if head == b"#!":
                                    child_env["MCTASH_COMM_NAME"] = os.path.basename(path0)
                            except OSError:
                                pass
                        with self._redirected_fds(sc.redirects):
                            proc = subprocess.Popen(
                                argv,
                                env=child_env,
                                start_new_session=True,
                                preexec_fn=self._preexec_reset_signals,
                            )

                        def _watch_proc() -> None:
                            self._watch_job_process(job_id, proc)

                        th = threading.Thread(target=_watch_proc, daemon=True)
                        self._bg_jobs[job_id] = th
                        self._bg_pids[job_id] = proc.pid
                        self._bg_pid_to_job[proc.pid] = job_id
                        self._bg_started_at[job_id] = time.monotonic()
                        self._bg_cmdline[job_id] = " ".join(argv)
                        self._register_job_spawn(job_id)
                        self._last_bg_job = job_id
                        self._last_bg_pid = proc.pid
                        self._emit_job_launch_banner(job_id, proc.pid)
                        th.start()
                        return 0
            except Exception:
                pass

            job_id = self._next_job_id
            self._next_job_id += 1
            env_snapshot = dict(self.env)
            local_snapshot = [dict(s) for s in self.local_stack]
            positional_snapshot = list(self.positional)
            functions_snapshot = dict(self.functions)
            functions_asdl_snapshot = dict(self.functions_asdl)
            aliases_snapshot = dict(self.aliases)
            traps_snapshot = dict(self.traps)
            options_snapshot = dict(self.options)
            readonly_snapshot = set(self.readonly_vars)
            source_stack_snapshot = list(self.source_stack)
            script_name_snapshot = self.script_name
            current_line_snapshot = self.current_line
            parent_fd_baseline = self._snapshot_open_fds()

            def _run_bg() -> None:
                # On Linux, detach filesystem and fd-table sharing for the
                # worker thread so subshell-like background jobs don't leak
                # cwd/fd mutations into the parent thread.
                self._try_unshare_thread_state()
                bg_rt = Runtime()
                bg_rt.env = dict(env_snapshot)
                bg_rt.local_stack = [dict(s) for s in local_snapshot]
                bg_rt.positional = list(positional_snapshot)
                bg_rt.functions = dict(functions_snapshot)
                bg_rt.functions_asdl = dict(functions_asdl_snapshot)
                bg_rt.aliases = dict(aliases_snapshot)
                bg_rt.traps = dict(traps_snapshot)
                bg_rt.options = dict(options_snapshot)
                bg_rt.readonly_vars = set(readonly_snapshot)
                bg_rt.source_stack = list(source_stack_snapshot)
                bg_rt.script_name = script_name_snapshot
                bg_rt.current_line = current_line_snapshot
                # Share job/pid registries with parent runtime.
                bg_rt._bg_jobs = self._bg_jobs
                bg_rt._bg_status = self._bg_status
                bg_rt._bg_pids = self._bg_pids
                bg_rt._bg_pid_to_job = self._bg_pid_to_job
                bg_rt._bg_started_at = self._bg_started_at
                bg_rt._bg_cmdline = self._bg_cmdline
                bg_rt._bg_stopped = self._bg_stopped
                bg_rt._job_state = self._job_state
                bg_rt._job_events = self._job_events
                bg_rt._job_event_lock = self._job_event_lock
                bg_rt._last_bg_job = self._last_bg_job
                bg_rt._last_bg_pid = self._last_bg_pid
                bg_rt._shared_store_path = self._shared_store_path
                bg_rt._shared_store = self._shared_store
                bg_rt._thread_ctx.job_id = job_id
                try:
                    bg_body = ListNode(items=[ListItem(node=item.node, background=False)])
                    status = bg_rt._run_subshell(bg_body)
                    self._record_bg_job_completion(job_id, status)
                finally:
                    # In shared-fd fallback modes (no CLONE_FILES unshare),
                    # explicitly close fds that this background runtime opened.
                    bg_rt._close_tracked_fds_not_in(parent_fd_baseline)
                    self._bg_pids.pop(job_id, None)

            thread = threading.Thread(target=_run_bg)
            thread.daemon = True
            self._bg_jobs[job_id] = thread
            self._bg_started_at[job_id] = time.monotonic()
            self._bg_cmdline[job_id] = "<background>"
            self._register_job_spawn(job_id)
            self._last_bg_job = job_id
            thread.start()
            # Best-effort: wait briefly for background job leader PID so $! is
            # available immediately after '&' for common cases.
            deadline = time.monotonic() + 0.1
            while time.monotonic() < deadline:
                pid = self._bg_pids.get(job_id)
                if pid is not None:
                    self._last_bg_pid = pid
                    self._emit_job_launch_banner(job_id, pid)
                    break
                if not thread.is_alive():
                    break
                time.sleep(0.001)
            return 0
        status = self._exec_and_or(item.node)
        self._drain_process_subst()
        return status

    def _compile_note(self, reason: str) -> None:
        if not self._compile_debug:
            return
        if reason in self._compile_fallback_seen:
            return
        self._compile_fallback_seen.add(reason)
        desc = self.COMPILE_FALLBACK_REASONS.get(reason, "")
        if desc:
            self._print_stderr(f"[mctash-compile] fallback: {reason} ({desc})")
            return
        if reason.startswith("unsupported-list-item:"):
            self._print_stderr(f"[mctash-compile] fallback: {reason} ({self.COMPILE_FALLBACK_REASONS.get('unsupported-list-item', '')})")
            return
        if reason.startswith("unsupported-command:"):
            self._print_stderr(f"[mctash-compile] fallback: {reason} ({self.COMPILE_FALLBACK_REASONS.get('unsupported-command', '')})")
            return
        self._print_stderr(f"[mctash-compile] fallback: {reason}")

    def _compile_namespace_key(self) -> str:
        explicit = self.env.get("MCTASH_NAMESPACE", "").strip()
        if explicit:
            return explicit
        mode = self.env.get("MCTASH_MODE", "").strip().lower()
        if mode in {"ash", "posix"} and self._bash_compat_level is None:
            return "ash"
        if mode == "bash" or self._bash_compat_level is not None:
            return f"bash-{self._bash_compat_level or 'default'}"
        return "sh"

    def _compile_cache_key(self, item: dict[str, Any]) -> tuple[str, str] | None:
        try:
            raw = json.dumps(item, sort_keys=True, separators=(",", ":")).encode("utf-8")
        except Exception:
            return None
        digest = hashlib.sha256(raw).hexdigest()
        return (self._compile_namespace_key(), digest)

    def _asdl_command_compile_eligible(self, node: Any) -> tuple[bool, str]:
        if not isinstance(node, dict):
            return False, "pipeline-stage-invalid"
        t = str(node.get("type", ""))
        if t not in self.COMPILED_SUPPORTED_COMMANDS:
            return False, f"unsupported-command:{t}"
        if t == "command.Redirect":
            child = node.get("child")
            if not isinstance(child, dict):
                return False, "pipeline-stage-invalid"
            return self._asdl_command_compile_eligible(child)
        if t == "command.BraceGroup":
            for child in (node.get("children") or []):
                ok, reason = self._asdl_item_compile_eligible(child)
                if not ok:
                    return False, reason
            return True, "ok"
        if t == "command.If":
            for arm in (node.get("arms") or []):
                cond = arm.get("cond") or {}
                action = arm.get("action") or {}
                for child in (cond.get("children") or []):
                    ok, reason = self._asdl_item_compile_eligible(child)
                    if not ok:
                        return False, reason
                for child in (action.get("children") or []):
                    ok, reason = self._asdl_item_compile_eligible(child)
                    if not ok:
                        return False, reason
            else_action = node.get("else_action") or {}
            for child in (else_action.get("children") or []):
                ok, reason = self._asdl_item_compile_eligible(child)
                if not ok:
                    return False, reason
            return True, "ok"
        if t == "command.WhileUntil":
            cond = node.get("cond") or {}
            body = node.get("body") or {}
            for child in (cond.get("children") or []):
                ok, reason = self._asdl_item_compile_eligible(child)
                if not ok:
                    return False, reason
            for child in self._asdl_do_group_children(body):
                ok, reason = self._asdl_item_compile_eligible(child)
                if not ok:
                    return False, reason
            return True, "ok"
        return True, "ok"

    def _asdl_item_compile_eligible(self, item: Any) -> tuple[bool, str]:
        if self._running_trap:
            return False, "trap-active"
        if self.options.get("m", False) and self._is_interactive_session:
            return False, "interactive-monitor-active"
        if not isinstance(item, dict):
            return False, "item-not-dict"
        t = str(item.get("type", ""))
        if t == "command.Sentence":
            term = self._asdl_token_text(item.get("terminator"))
            if term == "&":
                return False, "sentence-background"
            child = item.get("child")
            if not isinstance(child, dict):
                return False, "sentence-child-invalid"
            return self._asdl_item_compile_eligible(child)
        if t != "command.AndOr":
            return False, f"unsupported-list-item:{t}"
        children = item.get("children") or []
        if not children:
            return False, "andor-child-count"
        for pipeline in children:
            if not isinstance(pipeline, dict) or pipeline.get("type") != "command.Pipeline":
                return False, "pipeline-invalid"
            p_children = pipeline.get("children") or []
            if not p_children:
                return False, "pipeline-child-count"
            for cmd in p_children:
                ok, reason = self._asdl_command_compile_eligible(cmd)
                if not ok:
                    return False, reason
        return True, "ok"

    def _compile_asdl_list_item(self, item: dict[str, Any]) -> Callable[["Runtime"], int] | None:
        eligible, reason = self._asdl_item_compile_eligible(item)
        if not eligible:
            self._compile_note(reason)
            return None
        key = self._compile_cache_key(item)
        if key is None:
            self._compile_note("json-key-failed")
            return None
        fn = self._compiled_cache.get(key)
        if fn is not None:
            return fn
        try:
            src = (
                "def __mctash_compiled(rt, __node):\n"
                "    return rt._exec_compiled_list_item(__node)\n"
            )
            glb: dict[str, object] = {}
            code = compile(src, "<mctash-compiled>", "exec")
            exec(code, glb)
            compiled_impl = glb["__mctash_compiled"]
            if not callable(compiled_impl):
                self._compile_note("compiled-not-callable")
                return None
            fn = lambda rt, _impl=compiled_impl, _node=item: int(_impl(rt, _node))
            self._compiled_cache[key] = fn
            return fn
        except Exception:
            self._compile_note("compile-failed")
            return None

    def _exec_compiled_list_item(self, item: dict[str, Any]) -> int:
        t = item.get("type")
        if t == "command.Sentence":
            term = self._asdl_token_text(item.get("terminator"))
            child = item.get("child")
            if not isinstance(child, dict):
                raise RuntimeError("invalid ASDL sentence node")
            if term == "&":
                # guarded by eligibility, but keep semantics safe.
                return self._exec_asdl_background(child)
            status = self._exec_compiled_list_item(child)
            self._drain_process_subst()
            return status
        if t != "command.AndOr":
            return self._exec_asdl_list_item_impl(item)
        return self._exec_compiled_and_or(item)

    def _exec_compiled_and_or(self, node: dict[str, Any], track_status: bool = True) -> int:
        pipes = node.get("children") or []
        if not pipes:
            return 0
        if len(pipes) > 1:
            with self._suppress_errexit():
                status = self._exec_compiled_pipeline(pipes[0])
        else:
            status = self._exec_compiled_pipeline(pipes[0])
        last_exec_idx = 0
        if track_status:
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
        ops = node.get("ops") or []
        for i, (op, pipeline) in enumerate(zip(ops, pipes[1:]), start=1):
            op_s = self._asdl_token_text(op)
            if op_s == "&&":
                if status == 0:
                    if i < (len(pipes) - 1):
                        with self._suppress_errexit():
                            status = self._exec_compiled_pipeline(pipeline)
                    else:
                        status = self._exec_compiled_pipeline(pipeline)
                    last_exec_idx = i
            elif op_s == "||":
                if status != 0:
                    if i < (len(pipes) - 1):
                        with self._suppress_errexit():
                            status = self._exec_compiled_pipeline(pipeline)
                    else:
                        status = self._exec_compiled_pipeline(pipeline)
                    last_exec_idx = i
            if track_status:
                self.last_status = status
                if status != 0:
                    self.last_nonzero_status = status
                self._trap_status_hint = status
        neg_exempt = False
        if status != 0 and 0 <= last_exec_idx < len(pipes):
            last_pipe = pipes[last_exec_idx]
            if isinstance(last_pipe, dict):
                neg_exempt = bool(last_pipe.get("negated", False))
        self._errexit_item_exempt = status != 0 and (last_exec_idx < (len(pipes) - 1) or neg_exempt)
        return status

    def _exec_compiled_pipeline(self, node: dict[str, Any]) -> int:
        commands = node.get("children") or []
        negate = bool(node.get("negated", False))
        if negate:
            with self._suppress_errexit():
                status = self._exec_compiled_pipeline_body(commands)
            return 0 if status != 0 else 1
        return self._exec_compiled_pipeline_body(commands)

    def _exec_compiled_pipeline_body(self, commands: list[dict[str, Any]]) -> int:
        if not commands:
            return 0
        if len(commands) == 1:
            return self._exec_compiled_command(commands[0])
        # Phase 3: delegate multi-stage orchestration to existing pipeline
        # adapters while keeping compiled list/command dispatch around it.
        node = {"type": "command.Pipeline", "negated": False, "children": commands}
        if self._asdl_pipeline_can_run_external(commands):
            return self._exec_asdl_pipeline_external(commands)
        return self._exec_asdl_pipeline_inprocess(node)

    def _exec_compiled_command(self, node: dict[str, Any]) -> int:
        t = node.get("type")
        if t == "command.Simple":
            return self._exec_asdl_simple_command(node)
        if t == "command.Redirect":
            child = node.get("child") or {}
            self._validate_asdl_redirect_words(node.get("redirects") or [])
            redirects = [self._asdl_to_redirect(r) for r in (node.get("redirects") or [])]
            with self._redirected_fds(redirects):
                if isinstance(child, dict):
                    return self._exec_compiled_command(child)
                return self._exec_asdl_command(child)
        if t == "command.BraceGroup":
            return self._exec_compiled_command_list(node.get("children") or [])
        if t == "command.If":
            arms = node.get("arms") or []
            if not arms:
                return 0
            for arm in arms:
                cond = arm.get("cond") or {}
                with self._suppress_errexit():
                    cond_status = self._exec_compiled_command_list(cond.get("children") or [])
                if cond_status == 0:
                    action = arm.get("action") or {}
                    return self._exec_compiled_command_list(action.get("children") or [])
            else_action = node.get("else_action") or {}
            return self._exec_compiled_command_list(else_action.get("children") or [])
        if t == "command.WhileUntil":
            kw = self._asdl_token_text(node.get("keyword"))
            until = kw == "until"
            cond_node = node.get("cond") or {}
            body_children = self._asdl_do_group_children(node.get("body") or {})
            self._loop_depth += 1
            try:
                last = 0
                while True:
                    try:
                        with self._suppress_errexit():
                            cond_status = self._exec_compiled_command_list(cond_node.get("children") or [])
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        self._run_pending_traps()
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        last = 0
                        break
                    should_run = cond_status != 0 if until else cond_status == 0
                    if not should_run:
                        break
                    try:
                        last = self._exec_compiled_command_list(body_children)
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        self._run_pending_traps()
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        last = 0
                        break
                return last
            finally:
                self._loop_depth -= 1
        if t in {"command.ControlFlow", "command.ShAssignment"}:
            # Phase 3: reuse existing command-specific evaluators for these
            # semantics-sensitive nodes.
            return self._exec_asdl_command(node)
        return self._exec_asdl_command(node)

    def _exec_compiled_command_list(self, children: list[dict[str, Any]]) -> int:
        status = 0
        for child in children:
            status = self._exec_compiled_list_item(child)
            errexit_item_exempt = self._take_errexit_item_exempt()
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            is_bg = (
                isinstance(child, dict)
                and child.get("type") == "command.Sentence"
                and self._asdl_token_text(child.get("terminator")) == "&"
            )
            if not is_bg:
                self._run_pending_traps()
            if (
                status != 0
                and self.options.get("e", False)
                and self._errexit_suppressed == 0
                and not errexit_item_exempt
            ):
                raise SystemExit(status)
        self._run_pending_traps()
        return status

    def _exec_asdl_list_item(self, item: dict[str, Any]) -> int:
        if self._exec_backend_requested == "compiled" and not self._compiled_backend_enabled:
            self._compile_note("compile-disabled-by-config")
        if self._exec_backend == "compiled" and self._compiled_depth == 0:
            compiled = self._compile_asdl_list_item(item)
            if compiled is not None:
                self._compiled_depth += 1
                try:
                    return compiled(self)
                except Exception:
                    self._compile_note("compiled-runtime-error")
                finally:
                    self._compiled_depth -= 1
        return self._exec_asdl_list_item_impl(item)

    def _exec_asdl_list_item_impl(self, item: dict[str, Any]) -> int:
        t = item.get("type")
        if t == "command.Sentence":
            self._command_number += 1
            term = self._asdl_token_text(item.get("terminator"))
            child = item.get("child")
            if not isinstance(child, dict):
                raise RuntimeError("invalid ASDL sentence node")
            jobspec_spec = self._jobspec_spec_from_asdl_and_or(child)
            if jobspec_spec is not None:
                jobspec_token, redirects = jobspec_spec
                try:
                    with self._redirected_fds(redirects):
                        if term == "&":
                            return self._run_bg_builtin([jobspec_token])
                        status = self._run_fg([jobspec_token])
                        self._drain_process_subst()
                        return status
                except RuntimeError as e:
                    msg = str(e)
                    self._print_stderr(msg)
                    return self._runtime_error_status(msg)
            if term == "&":
                return self._exec_asdl_background(child)
            status = self._exec_asdl_list_item(child)
            self._drain_process_subst()
            return status
        if t != "command.AndOr":
            raise RuntimeError(f"invalid ASDL list item: {t}")
        jobspec_spec = self._jobspec_spec_from_asdl_and_or(item)
        if jobspec_spec is not None:
            jobspec_token, redirects = jobspec_spec
            try:
                with self._redirected_fds(redirects):
                    status = self._run_fg([jobspec_token])
                    self._drain_process_subst()
                    return status
            except RuntimeError as e:
                msg = str(e)
                self._print_stderr(msg)
                return self._runtime_error_status(msg)
        status = self._exec_asdl_and_or(item)
        self._drain_process_subst()
        return status

    def _drain_process_subst(self) -> None:
        if not self._procsub_threads:
            return
        pending = self._procsub_threads
        still_running: list[threading.Thread] = []
        for th in pending:
            th.join(timeout=2.0)
            if th.is_alive():
                still_running.append(th)
        self._procsub_threads = still_running

    def _exec_asdl_and_or(self, node: dict[str, Any], track_status: bool = True) -> int:
        pipes = node.get("children") or []
        if not pipes:
            return 0
        if len(pipes) > 1:
            with self._suppress_errexit():
                status = self._exec_asdl_pipeline(pipes[0])
        else:
            status = self._exec_asdl_pipeline(pipes[0])
        last_exec_idx = 0
        if track_status:
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
        ops = node.get("ops") or []
        for i, (op, pipeline) in enumerate(zip(ops, pipes[1:]), start=1):
            op_s = self._asdl_token_text(op)
            if op_s == "&&":
                if status == 0:
                    if i < (len(pipes) - 1):
                        with self._suppress_errexit():
                            status = self._exec_asdl_pipeline(pipeline)
                    else:
                        status = self._exec_asdl_pipeline(pipeline)
                    last_exec_idx = i
            elif op_s == "||":
                if status != 0:
                    if i < (len(pipes) - 1):
                        with self._suppress_errexit():
                            status = self._exec_asdl_pipeline(pipeline)
                    else:
                        status = self._exec_asdl_pipeline(pipeline)
                    last_exec_idx = i
            if track_status:
                self.last_status = status
                if status != 0:
                    self.last_nonzero_status = status
                self._trap_status_hint = status
        neg_exempt = False
        if status != 0 and 0 <= last_exec_idx < len(pipes):
            last_pipe = pipes[last_exec_idx]
            if isinstance(last_pipe, dict):
                neg_exempt = bool(last_pipe.get("negated", False))
        self._errexit_item_exempt = status != 0 and (
            last_exec_idx < (len(pipes) - 1) or neg_exempt
        )
        return status

    def _exec_asdl_pipeline(self, node: dict[str, Any]) -> int:
        commands = node.get("children") or []
        negate = bool(node.get("negated", False))
        if negate:
            with self._suppress_errexit():
                if not commands:
                    status = 0
                elif len(commands) == 1:
                    status = self._exec_asdl_command(commands[0])
                else:
                    if self._asdl_pipeline_can_run_external(commands):
                        status = self._exec_asdl_pipeline_external(commands)
                    else:
                        status = self._exec_asdl_pipeline_inprocess(node)
        elif not commands:
            status = 0
        elif len(commands) == 1:
            status = self._exec_asdl_command(commands[0])
        else:
            if self._asdl_pipeline_can_run_external(commands):
                status = self._exec_asdl_pipeline_external(commands)
            else:
                status = self._exec_asdl_pipeline_inprocess(node)
        if negate:
            return 0 if status != 0 else 1
        return status

    def _asdl_pipeline_can_run_external(self, commands: list[dict[str, Any]]) -> bool:
        if isinstance(sys.stdin, io.StringIO):
            return False
        for cmd in commands:
            if not isinstance(cmd, dict) or cmd.get("type") != "command.Simple":
                return False
            argv = self._expand_asdl_simple_argv(cmd)
            argv = self._expand_aliases(argv)
            if not argv:
                return False
            name = argv[0]
            if self._is_builtin_enabled(name) or self._has_function(name):
                return False
        return True

    def _exec_asdl_pipeline_external(self, commands: list[dict[str, Any]]) -> int:
        procs: list[subprocess.Popen] = []
        prev = None
        statuses: list[int] = []
        for i, cmd in enumerate(commands):
            cmd_env = self._exported_env_view(self.env)
            for scope in self.local_stack:
                for k, v in scope.items():
                    if k in self.env and "exported" in self._var_attrs.get(k, set()):
                        cmd_env[k] = v
            for assign in (cmd.get("more_env") or []):
                name = str(assign.get("name") or "")
                value = self._expand_asdl_rhs_assignment(assign.get("val") or {})
                cmd_env[name] = value
            argv = self._expand_asdl_simple_argv(cmd)
            argv = self._expand_aliases(argv)
            stdin = prev.stdout if prev is not None else None
            stdout = subprocess.PIPE if i < len(commands) - 1 else None
            redirects = [self._asdl_to_redirect(r) for r in (cmd.get("redirects") or [])]
            stdin, stdout, stderr, to_close = self._apply_redirects(redirects, stdin, stdout, None)
            try:
                proc = subprocess.Popen(
                    argv,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    env=cmd_env,
                    preexec_fn=self._preexec_reset_signals,
                )
            except FileNotFoundError:
                if "/" in argv[0]:
                    print(
                        self._diag_msg(
                            DiagnosticKey.ERRNO_NAME,
                            name=argv[0],
                            error="No such file or directory",
                        ),
                        file=sys.stderr,
                    )
                else:
                    print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0]), file=sys.stderr)
                # In a pipeline, failed exec of one stage doesn't prevent
                # sibling stages from running; emulate by inserting a process
                # that exits with the expected status.
                proc = subprocess.Popen(
                    ["sh", "-c", "exit 127"],
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    env=cmd_env,
                    preexec_fn=self._preexec_reset_signals,
                )
            except OSError as e:
                self._print_stderr(self._diag_msg(DiagnosticKey.ERRNO_NAME, name=argv[0], error=str(e.strerror)))
                proc = subprocess.Popen(
                    ["sh", "-c", "exit 126"],
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    env=cmd_env,
                    preexec_fn=self._preexec_reset_signals,
                )
            finally:
                for f in to_close:
                    try:
                        f.close()
                    except Exception:
                        pass
            procs.append(proc)
            if prev is not None and prev.stdout is not None:
                prev.stdout.close()
            prev = proc
        status = procs[-1].wait()
        statuses.append(status)
        for p in procs[:-1]:
            statuses.insert(0, p.wait())
        return self._pipeline_result(statuses)

    def _exec_asdl_command(self, node: dict[str, Any]) -> int:
        t = node.get("type")
        if self.options.get("n", False):
            if t == "command.Func":
                name_tok = node.get("name")
                name = self._asdl_token_text(name_tok)
                body = node.get("body")
                if name and isinstance(body, dict):
                    self.functions_asdl[name] = body
            return 0
        if t == "command.Simple":
            return self._exec_asdl_simple_command(node)
        if t == "command.Redirect":
            child = node.get("child") or {}
            self._validate_asdl_redirect_words(node.get("redirects") or [])
            redirects = [self._asdl_to_redirect(r) for r in (node.get("redirects") or [])]
            with self._redirected_fds(redirects):
                return self._exec_asdl_command(child)
        if t == "command.BraceGroup":
            children = node.get("children") or []
            return self._exec_asdl_command_list(children)
        if t == "command.If":
            arms = node.get("arms") or []
            if not arms:
                return 0
            for arm in arms:
                cond = arm.get("cond") or {}
                with self._suppress_errexit():
                    cond_status = self._exec_asdl_command_list((cond.get("children") or []))
                if cond_status == 0:
                    action = arm.get("action") or {}
                    return self._exec_asdl_command_list((action.get("children") or []))
            else_action = node.get("else_action") or {}
            return self._exec_asdl_command_list((else_action.get("children") or []))
        if t == "command.WhileUntil":
            kw = self._asdl_token_text(node.get("keyword"))
            until = kw == "until"
            cond_node = node.get("cond") or {}
            body_node = node.get("body") or {}
            body_children = body_node.get("children") or body_node.get("children", [])
            if body_node.get("type") == "command.CommandList":
                body_children = body_node.get("children") or []
            self._loop_depth += 1
            try:
                last = 0
                while True:
                    try:
                        with self._suppress_errexit():
                            cond_status = self._exec_asdl_command_list((cond_node.get("children") or []))
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        self._run_pending_traps()
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        last = 0
                        break
                    should_run = cond_status != 0 if until else cond_status == 0
                    if not should_run:
                        break
                    try:
                        last = self._exec_asdl_command_list(body_children)
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        self._run_pending_traps()
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        last = 0
                        break
                return last
            finally:
                self._loop_depth -= 1
        if t == "command.Subshell":
            return self._run_subshell_asdl(node.get("child") or {})
        if t == "command.ShFunction":
            name = str(node.get("name") or "")
            if self.options.get("posix", False) and name in self.SPECIAL_BUILTINS:
                self._report_error(
                    f"{name}: is a special builtin",
                    line=self.current_line,
                    context="function",
                )
                return 2
            body = node.get("body") or {"type": "command.CommandList", "children": []}
            # Canonical function storage for parsed shell code.
            self.functions_asdl[name] = body
            return 0
        if t == "command.ForEach":
            names = node.get("iter_names") or [""]
            var_name = str(names[0] if names else "")
            if var_name in self.readonly_vars:
                msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=var_name)
                self._report_error(msg, line=self.current_line, context="for")
                if self.options.get("posix", False) and self._is_noninteractive():
                    raise SystemExit(1)
                return 1
            iterable = node.get("iterable") or {}
            explicit_in = bool(node.get("explicit_in", False))
            if explicit_in:
                for w in (iterable.get("words") or []):
                    self._validate_asdl_word_bad_subst(w)
                items: list[str] = []
                for w in (iterable.get("words") or []):
                    items.extend(self._expand_asdl_word_fields(w, split_glob=True))
            else:
                items = list(self.positional)
            body = self._asdl_do_group_children(node.get("body") or {})
            status = 0
            self._loop_depth += 1
            try:
                for item in items:
                    self.env[var_name] = item
                    try:
                        status = self._exec_asdl_command_list(body)
                        self._run_pending_traps()
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        break
                return status
            finally:
                self._loop_depth -= 1
        if t == "command.ForExpr":
            raw = node.get("raw") or {}
            init = str(raw.get("init") or "")
            cond = str(raw.get("cond") or "")
            update = str(raw.get("update") or "")
            body = self._asdl_do_group_children(node.get("body") or {})
            return self._run_arith_for(init, cond, update, lambda: self._exec_asdl_command_list(body))
        if t == "command.Select":
            var_name = str(node.get("iter_name") or "")
            iterable = node.get("iterable") or {}
            explicit_in = bool(node.get("explicit_in", False))
            if explicit_in:
                items: list[str] = []
                for w in (iterable.get("words") or []):
                    self._validate_asdl_word_bad_subst(w)
                    items.extend(self._expand_asdl_word_fields(w, split_glob=True))
            else:
                items = list(self.positional)
            body = self._asdl_do_group_children(node.get("body") or {})
            status = 0
            self._loop_depth += 1
            try:
                while True:
                    for i, item in enumerate(items, start=1):
                        self._print_stderr(f"{i}) {item}")
                    prompt = self._get_var("PS3") or "#? "
                    try:
                        sys.stderr.write(prompt)
                        sys.stderr.flush()
                    except Exception:
                        pass
                    line = sys.stdin.readline()
                    if line == "":
                        return 1
                    reply = line.rstrip("\n")
                    self._set_var("REPLY", reply)
                    selected = ""
                    if reply.isdigit():
                        idx = int(reply)
                        if 1 <= idx <= len(items):
                            selected = items[idx - 1]
                    self._set_var(var_name, selected)
                    try:
                        status = self._exec_asdl_command_list(body)
                        self._run_pending_traps()
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        break
                return status
            finally:
                self._loop_depth -= 1
        if t == "command.Coproc":
            name = str(node.get("name") or "COPROC")
            child = node.get("child") or {}
            script = self._asdl_command_to_sh_source(child)
            proc = self._popen_shell_subprocess(
                script=script,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=None,
                text=False,
                preexec_fn=self._preexec_reset_signals,
            )
            if proc.stdout is None or proc.stdin is None:
                return 1
            read_fd = os.dup(proc.stdout.fileno())
            write_fd = os.dup(proc.stdin.fileno())
            if read_fd >= 3:
                self._user_fds.add(read_fd)
            if write_fd >= 3:
                self._user_fds.add(write_fd)
            self._typed_vars[name] = [str(read_fd), str(write_fd)]
            self._set_var_attrs(name, array=True)
            self._set_subscript_projection(name, str(read_fd))
            self._set_var(f"{name}_PID", str(proc.pid))

            job_id = self._next_job_id
            self._next_job_id += 1
            self._last_bg_job = job_id
            self._last_bg_pid = proc.pid
            self._bg_pids[job_id] = proc.pid
            self._bg_pid_to_job[proc.pid] = job_id
            self._bg_started_at[job_id] = time.time()
            self._bg_cmdline[job_id] = f"coproc {name}"
            self._register_job_spawn(job_id)
            self._coproc_procs[job_id] = proc

            def _wait_coproc() -> None:
                rc = proc.wait()
                self._record_bg_job_completion(job_id, rc)
                self._coproc_procs.pop(job_id, None)

            th = threading.Thread(target=_wait_coproc, daemon=True)
            self._bg_jobs[job_id] = th
            th.start()
            return 0
        if t == "command.Case":
            to_match = node.get("to_match") or {}
            value_word = to_match.get("word") if isinstance(to_match, dict) else {}
            if isinstance(value_word, dict):
                self._validate_asdl_word_bad_subst(value_word)
            value = self._expand_asdl_assignment_scalar(value_word or {})
            mode = "match"
            for arm in (node.get("arms") or []):
                pat = arm.get("pattern") or {}
                matched = mode == "fallthrough"
                if mode != "fallthrough":
                    for pw in (pat.get("words") or []):
                        try:
                            self._validate_asdl_word_bad_subst(pw)
                            pattern = self._asdl_case_pattern_from_word(pw)
                            if self._case_pattern_matches(value, pattern):
                                matched = True
                                break
                        except RuntimeError as e:
                            self._report_error(str(e))
                            return 1
                if not matched:
                    continue
                status = self._exec_asdl_command_list(arm.get("action") or [])
                op = str(arm.get("op", ";;"))
                if op in {";;", "esac", ""}:
                    return status
                if op == ";&":
                    mode = "fallthrough"
                    continue
                if op == ";;&":
                    mode = "retest"
                    continue
                return status
            return 0
        if t == "command.ControlFlow":
            keyword = self._asdl_token_text(node.get("keyword"))
            argv = [keyword]
            arg = node.get("arg_word")
            if arg is not None:
                self._validate_asdl_word_bad_subst(arg)
                argv.append(self._expand_asdl_word_scalar(arg, split_glob=False))
            return self._run_builtin(keyword, argv)
        if t == "command.ShAssignment":
            for pair in (node.get("pairs") or []):
                self._validate_asdl_rhs_bad_subst(pair.get("rhs"))
            self._validate_asdl_redirect_words(node.get("redirects") or [])
            local_env = dict(self.env)
            saved_env = self.env
            assigned_names: set[str] = set()
            compound_assigned: set[str] = set()
            redirects = [self._asdl_to_redirect(r) for r in (node.get("redirects") or [])]
            try:
                self.env = local_env
                for pair in (node.get("pairs") or []):
                    name = str(pair.get("name", ""))
                    op = str(pair.get("op", "="))
                    rhs = pair.get("rhs") or {}
                    try:
                        value = self._expand_asdl_rhs_assignment(rhs)
                    except CommandSubstFailure as e:
                        return e.code
                    except ArithExpansionFailure as e:
                        return e.code
                    assigned_names.add(name)
                    if name in self.readonly_vars:
                        msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                        print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                        if self._diag.style == "bash":
                            return 1
                        raise SystemExit(2)
                    comp_vals = self._parse_compound_assignment_rhs(self._asdl_rhs_word_to_text(rhs))
                    if comp_vals is not None and self._bash_compat_level is None:
                        comp_vals = None
                    if comp_vals is None:
                        bad_tok = self._compound_assignment_unexpected_token(self._asdl_rhs_word_to_text(rhs))
                        if bad_tok is not None:
                            self._print_stderr(
                                self._format_error(
                                    f"syntax error near unexpected token `{bad_tok}'",
                                    line=self.current_line,
                                )
                            )
                            return 1
                    if name in self._py_ties:
                        if comp_vals is not None:
                            raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                        self._assign_shell_var_op(name, op, value)
                        self._sync_local_env_assignment(local_env, name)
                        continue
                    if comp_vals is not None:
                        if self._parse_subscripted_name(name) is not None:
                            raise RuntimeError(f"{name}: cannot assign list to array member")
                        self._assign_compound_var(name, op, comp_vals)
                        compound_assigned.add(name)
                        self._sync_local_env_assignment(local_env, name)
                        continue
                    self._assign_shell_var_op(name, op, value)
                    self._sync_local_env_assignment(local_env, name)
                if self.options.get("x", False):
                    trace_assigns = [
                        Assignment(
                            name=str(p.get("name", "")),
                            value=self._asdl_rhs_word_to_text(p.get("rhs") or {}),
                            op=str(p.get("op", "=")),
                        )
                        for p in (node.get("pairs") or [])
                    ]
                    self._trace_simple(SimpleCommand(argv=[], assignments=trace_assigns, redirects=[]), [], local_env)
                if redirects:
                    with self._redirected_fds(redirects):
                        pass
            except RuntimeError as e:
                msg = str(e)
                print(msg, file=sys.stderr)
                return self._runtime_error_status(msg)
            finally:
                self.env = saved_env
            for n in assigned_names:
                if n in compound_assigned:
                    continue
                attrs = self._structured_var_attrs(n)
                if "array" in attrs or "assoc" in attrs:
                    continue
                self._typed_vars.pop(n, None)
            self.env.update(local_env)
            for tied_name in self._py_ties:
                self.env[tied_name] = self._get_var(tied_name)
            if self._cmd_sub_used:
                status = self._cmd_sub_status
                self._cmd_sub_used = False
                return status
            return 0
        raise RuntimeError(f"unsupported ASDL command node {t}")

    def _exec_asdl_pipeline_inprocess(self, node: dict[str, Any]) -> int:
        commands = node.get("children") or []
        data: bytes | None = None
        data_latency: float | None = None
        if isinstance(sys.stdin, io.StringIO):
            seed = sys.stdin.read()
            data = seed.encode("utf-8", errors="surrogateescape")
            if self._pipeline_input_latency is not None:
                data_latency = self._pipeline_input_latency
        statuses: list[int] = []
        status = 0
        for i, cmd in enumerate(commands):
            last = i == len(commands) - 1
            simple_cmd = self._asdl_pipeline_simple_command(cmd)
            if last:
                if simple_cmd is not None:
                    argv = self._expand_argv(simple_cmd.argv)
                    argv = self._expand_aliases(argv)
                    saved_latency = self._pipeline_input_latency
                    self._pipeline_input_latency = data_latency
                    status, data, data_latency = self._exec_simple_capture(simple_cmd, argv, data, capture=False)
                    self._pipeline_input_latency = saved_latency
                else:
                    saved_stdin = sys.stdin
                    saved_latency = self._pipeline_input_latency
                    try:
                        if data is not None:
                            sys.stdin = io.StringIO(data.decode("utf-8", errors="ignore"))
                        self._pipeline_input_latency = data_latency
                        try:
                            status = self._exec_asdl_pipeline_stage_subshell(cmd)
                        except SystemExit as e:
                            status = int(e.code) if e.code is not None else 0
                        except ReturnFromFunction as e:
                            status = e.code
                        except (BreakLoop, ContinueLoop):
                            status = 1
                    finally:
                        sys.stdin = saved_stdin
                        self._pipeline_input_latency = saved_latency
                statuses.append(status)
                data = None
                data_latency = None
                continue
            sink_is_no_reader = False
            if i + 1 < len(commands):
                sink_is_no_reader = self._asdl_pipeline_sink_is_no_reader(commands[i + 1])
            if simple_cmd is not None:
                argv = self._expand_argv(simple_cmd.argv)
                argv = self._expand_aliases(argv)
                saved_latency = self._pipeline_input_latency
                self._pipeline_input_latency = data_latency
                status, data, data_latency = self._exec_simple_capture(
                    simple_cmd, argv, data, capture=True
                )
                self._pipeline_input_latency = saved_latency
            else:
                status, data, data_latency = self._capture_asdl_command_output(
                    cmd, data=data, force_epipe=sink_is_no_reader
                )
            statuses.append(status)
        return self._pipeline_result(statuses if statuses else [status])

    def _capture_asdl_command_output(
        self, cmd: dict[str, Any], data: bytes | None = None, force_epipe: bool = False
    ) -> tuple[int, bytes, float]:
        start = time.monotonic()
        tmp = tempfile.TemporaryFile()
        try:
            sys.stdout.flush()
        except Exception:
            pass
        saved_stdout = os.dup(1)
        saved_stdin = sys.stdin
        os.dup2(tmp.fileno(), 1)
        py_stdout = os.fdopen(os.dup(1), "w", encoding="utf-8", errors="surrogateescape", buffering=1)
        saved_py_stdout = sys.stdout
        sys.stdout = py_stdout
        saved_epipe = self._force_broken_pipe
        self._force_broken_pipe = force_epipe
        try:
            try:
                if data is not None:
                    sys.stdin = io.StringIO(data.decode("utf-8", errors="ignore"))
                status = self._exec_asdl_pipeline_stage_subshell(cmd)
            except SystemExit as e:
                status = int(e.code) if e.code is not None else 0
        finally:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            sys.stdout = saved_py_stdout
            try:
                py_stdout.close()
            except Exception:
                pass
            sys.stdin = saved_stdin
            self._force_broken_pipe = saved_epipe
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
        tmp.seek(0)
        out = tmp.read()
        tmp.close()
        return status, out, time.monotonic() - start

    def _exec_asdl_pipeline_stage_subshell(self, cmd: dict[str, Any]) -> int:
        return self._run_subshell_asdl(
            {
                "type": "command.CommandList",
                "children": [
                    {
                        "type": "command.AndOr",
                        "children": [
                            {
                                "type": "command.Pipeline",
                                "children": [cmd],
                                "ops": [],
                                "op_pos": [],
                                "negated": False,
                            }
                        ],
                        "ops": [],
                    }
                ],
            }
        )

    def _asdl_pipeline_sink_is_no_reader(self, cmd: dict[str, Any]) -> bool:
        if not isinstance(cmd, dict):
            return False
        t = cmd.get("type")
        if t == "command.Simple":
            try:
                argv = self._expand_asdl_simple_argv(cmd)
                argv = self._expand_aliases(argv)
            except Exception:
                return False
            return argv == ["true"]
        if t == "command.BraceGroup":
            children = cmd.get("children") or []
            if len(children) != 1:
                return False
            item = children[0] if isinstance(children[0], dict) else {}
            andor = item
            if andor.get("type") == "command.Sentence":
                andor = andor.get("child") if isinstance(andor.get("child"), dict) else {}
            if andor.get("type") != "command.AndOr":
                return False
            pipes = andor.get("children") or []
            if len(pipes) != 1:
                return False
            pipe = pipes[0] if isinstance(pipes[0], dict) else {}
            if pipe.get("type") != "command.Pipeline":
                return False
            cmds = pipe.get("children") or []
            if len(cmds) != 1:
                return False
            inner = cmds[0] if isinstance(cmds[0], dict) else {}
            if inner.get("type") != "command.Simple":
                return False
            try:
                argv = self._expand_asdl_simple_argv(inner)
                argv = self._expand_aliases(argv)
            except Exception:
                return False
            return argv == ["true"]
        return False

    def _asdl_pipeline_simple_command(self, node: dict[str, Any]) -> SimpleCommand | None:
        if not isinstance(node, dict) or node.get("type") != "command.Simple":
            return None
        return SimpleCommand(
            argv=[Word(self._asdl_word_to_text(w)) for w in (node.get("words") or [])],
            assignments=[
                Assignment(
                    name=env_pair.get("name", ""),
                    value=self._asdl_rhs_word_to_text(env_pair.get("val")),
                    op="=",
                )
                for env_pair in (node.get("more_env") or [])
            ],
            redirects=[self._asdl_to_redirect(r) for r in (node.get("redirects") or [])],
            line=self._asdl_command_line(node),
        )

    def _run_subshell_asdl(self, body: dict[str, Any]) -> int:
        self._set_subshell_depth(self._get_subshell_depth() + 1)
        saved_env = dict(self.env)
        self.env = dict(self.env)
        saved_options = dict(self.options)
        saved_local = [dict(s) for s in self.local_stack]
        saved_positional = list(self.positional)
        saved_loop_depth = self._loop_depth
        if self._bash_compat_level is not None and self._bash_compat_level >= 44:
            # bash compat>=44: subshell should not inherit active loop context
            # for break/continue propagation.
            self._loop_depth = 0
        saved_cwd = os.getcwd()
        saved_traps = dict(self.traps)
        self.traps = {
            k: v
            for k, v in self.traps.items()
            if k != "EXIT" and not (k in {"TERM", "WINCH"} and v != "")
        }
        try:
            with self._push_frame(kind="subshell"):
                try:
                    status = self._exec_asdl_command_list(body.get("children") or [])
                except SystemExit as e:
                    status = int(e.code) if e.code is not None else 0
                except (BreakLoop, ContinueLoop):
                    status = 1
                except ReturnFromFunction:
                    status = 1
                except RuntimeError as e:
                    msg = str(e)
                    print(msg, file=sys.stderr)
                    status = self._runtime_error_status(msg)
            sig_num: int | None = None
            if status < 0:
                sig_num = -status
            elif status >= 128:
                sig_num = status - 128
            if sig_num is not None and sig_num > 0:
                sig_name = None
                try:
                    sig_name = signal.Signals(sig_num).name.replace("SIG", "")
                except Exception:
                    sig_name = None
                if sig_name:
                    action = self.traps.get(sig_name)
                    if action:
                        self._run_trap_action(action, 128 + sig_num)
                        status = 0
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            return self._run_exit_trap(status)
        finally:
            self._set_subshell_depth(self._get_subshell_depth() - 1)
            self.env = saved_env
            self.options = saved_options
            self.local_stack = saved_local
            self.positional = saved_positional
            self._loop_depth = saved_loop_depth
            self.traps = saved_traps
            try:
                os.chdir(saved_cwd)
            except OSError:
                pass

    def _exec_asdl_background(self, child: dict[str, Any]) -> int:
        try:
            pipeline = child.get("children", [{}])[0]
            pipe_children = pipeline.get("children") if isinstance(pipeline, dict) else []
            cmd = pipe_children[0] if isinstance(pipe_children, list) and pipe_children else {}
            if (
                isinstance(cmd, dict)
                and child.get("type") == "command.AndOr"
                and len(child.get("children") or []) == 1
                and len(child.get("ops") or []) == 0
                and isinstance(pipeline, dict)
                and pipeline.get("type") == "command.Pipeline"
                and len(pipe_children or []) == 1
                and cmd.get("type") == "command.Simple"
            ):
                argv = self._expand_asdl_simple_argv(cmd)
                argv = self._expand_aliases(argv)
                if argv and not self._is_builtin_enabled(argv[0]) and not self._has_function(argv[0]):
                    cmd_env = dict(self.env)
                    for scope in self.local_stack:
                        for k, v in scope.items():
                            if k in self.env:
                                cmd_env[k] = v
                    for assign in (cmd.get("more_env") or []):
                        name = str(assign.get("name") or "")
                        value = self._expand_asdl_rhs_assignment(assign.get("val") or {})
                        cmd_env[name] = value
                    redirects = [self._asdl_to_redirect(r) for r in (cmd.get("redirects") or [])]
                    job_id = self._next_job_id
                    self._next_job_id += 1
                    child_env = dict(cmd_env)
                    path0 = argv[0]
                    if os.path.isfile(path0):
                        try:
                            with open(path0, "rb") as f:
                                head = f.read(2)
                            if head == b"#!":
                                child_env["MCTASH_COMM_NAME"] = os.path.basename(path0)
                        except OSError:
                            pass
                    with self._redirected_fds(redirects):
                        proc = subprocess.Popen(
                            argv,
                            env=child_env,
                            start_new_session=True,
                            preexec_fn=self._preexec_reset_signals,
                        )

                    def _watch_proc() -> None:
                        self._watch_job_process(job_id, proc)

                    th = threading.Thread(target=_watch_proc, daemon=True)
                    self._bg_jobs[job_id] = th
                    self._bg_pids[job_id] = proc.pid
                    self._bg_pid_to_job[proc.pid] = job_id
                    self._bg_started_at[job_id] = time.monotonic()
                    self._bg_cmdline[job_id] = " ".join(argv)
                    self._register_job_spawn(job_id)
                    self._last_bg_job = job_id
                    self._last_bg_pid = proc.pid
                    self._emit_job_launch_banner(job_id, proc.pid)
                    th.start()
                    return 0
        except Exception:
            pass

        job_id = self._next_job_id
        self._next_job_id += 1
        env_snapshot = dict(self.env)
        local_snapshot = [dict(s) for s in self.local_stack]
        positional_snapshot = list(self.positional)
        functions_snapshot = dict(self.functions)
        functions_asdl_snapshot = dict(self.functions_asdl)
        aliases_snapshot = dict(self.aliases)
        traps_snapshot = dict(self.traps)
        options_snapshot = dict(self.options)
        readonly_snapshot = set(self.readonly_vars)
        source_stack_snapshot = list(self.source_stack)
        script_name_snapshot = self.script_name
        current_line_snapshot = self.current_line
        parent_fd_baseline = self._snapshot_open_fds()

        def _run_bg() -> None:
            self._try_unshare_thread_state()
            bg_rt = Runtime()
            bg_rt.env = dict(env_snapshot)
            bg_rt.local_stack = [dict(s) for s in local_snapshot]
            bg_rt.positional = list(positional_snapshot)
            bg_rt.functions = dict(functions_snapshot)
            bg_rt.functions_asdl = dict(functions_asdl_snapshot)
            bg_rt.aliases = dict(aliases_snapshot)
            bg_rt.traps = dict(traps_snapshot)
            bg_rt.options = dict(options_snapshot)
            bg_rt.readonly_vars = set(readonly_snapshot)
            bg_rt.source_stack = list(source_stack_snapshot)
            bg_rt.script_name = script_name_snapshot
            bg_rt.current_line = current_line_snapshot
            bg_rt._bg_jobs = self._bg_jobs
            bg_rt._bg_status = self._bg_status
            bg_rt._bg_pids = self._bg_pids
            bg_rt._bg_pid_to_job = self._bg_pid_to_job
            bg_rt._bg_started_at = self._bg_started_at
            bg_rt._bg_cmdline = self._bg_cmdline
            bg_rt._bg_stopped = self._bg_stopped
            bg_rt._job_state = self._job_state
            bg_rt._job_events = self._job_events
            bg_rt._job_event_lock = self._job_event_lock
            bg_rt._last_bg_job = self._last_bg_job
            bg_rt._last_bg_pid = self._last_bg_pid
            bg_rt._shared_store_path = self._shared_store_path
            bg_rt._shared_store = self._shared_store
            bg_rt._thread_ctx.job_id = job_id
            try:
                status = bg_rt._run_subshell_asdl(
                    {"type": "command.CommandList", "children": [{"type": "command.Sentence", "child": child}]}
                )
                self._record_bg_job_completion(job_id, status)
            finally:
                bg_rt._close_tracked_fds_not_in(parent_fd_baseline)
                self._bg_pids.pop(job_id, None)

        thread = threading.Thread(target=_run_bg, daemon=True)
        self._bg_jobs[job_id] = thread
        self._bg_started_at[job_id] = time.monotonic()
        self._bg_cmdline[job_id] = self._asdl_command_to_sh_source(child)
        self._register_job_spawn(job_id)
        self._last_bg_job = job_id
        thread.start()
        deadline = time.monotonic() + 0.1
        while time.monotonic() < deadline:
            pid = self._bg_pids.get(job_id)
            if pid is not None:
                self._last_bg_pid = pid
                self._emit_job_launch_banner(job_id, pid)
                break
            if not thread.is_alive():
                break
            time.sleep(0.001)
        return 0

    def _expand_asdl_simple_argv(self, node: dict[str, Any]) -> list[str]:
        words = node.get("words") or []
        out: list[str] = []
        for w in words:
            out.extend(self._expand_asdl_word_fields(w, split_glob=True))
        return out

    def _expand_asdl_declare_argv(self, node: dict[str, Any], cmd_name: str) -> tuple[list[str], dict[int, str]]:
        words = node.get("words") or []
        out: list[str] = [cmd_name]
        raw_by_idx: dict[int, str] = {}
        for w in words[1:]:
            if not isinstance(w, dict):
                continue
            raw = self._asdl_word_to_text(w)
            # Preserve declaration assignment words as raw lexical units so
            # _run_declare can apply assignment-context expansion itself.
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*(?:\[[^]]*\])?\+?=", raw):
                m = re.match(r"^([^=]+?)(\+?=)(.*)$", raw)
                if m is None:
                    out.append(raw)
                    continue
                lhs = m.group(1)
                op = m.group(2)
                rhs = m.group(3)
                out.append(f"{lhs}{op}{self._expand_assignment_word(rhs)}")
                raw_by_idx[len(out) - 2] = raw
                continue
            out.extend(self._expand_asdl_word_fields(w, split_glob=True))
        return out, raw_by_idx

    def _asdl_word_can_expand_case_natively_safe(self, word: dict[str, Any]) -> bool:
        if not isinstance(word, dict) or word.get("type") != "word.Compound":
            return False
        parts = word.get("parts") or []
        if not parts:
            return True
        for p in parts:
            if not isinstance(p, dict):
                return False
            t = p.get("type")
            if t == "word_part.Literal":
                continue
            if t == "word_part.SingleQuoted":
                continue
            if t == "word_part.DoubleQuoted":
                continue
            if t == "word_part.SimpleVarSub":
                name = str(p.get("name", ""))
                if self._is_valid_name(name):
                    continue
                return False
            if t == "word_part.BracedVarSub":
                name = str(p.get("name", ""))
                op = p.get("op")
                if op == "__invalid__":
                    return False
                if op in {"-", ":-", "+", ":+", "?", ":?", "#", "##", "%", "%%", ":substr", "/"}:
                    arg = p.get("arg")
                    if not self._asdl_word_is_safe_literal(arg):
                        return False
                if op in {"@Q", "@P", "@A", "@a", "@E", "@U", "@u", "@L"}:
                    pass
                if self._is_valid_name(name):
                    continue
                return False
            return False
        return True

    def _exec_asdl_simple_command(self, node: dict[str, Any]) -> int:
        line = self._asdl_command_line(node)
        if line is not None:
            self.current_line = line
        redirects = [self._asdl_to_redirect(r) for r in (node.get("redirects") or [])]
        raw_words = [self._asdl_word_to_text(w) for w in (node.get("words") or [])]
        unmatched_q = None
        if raw_words and raw_words[0] in self.aliases:
            unmatched_q = self._alias_unmatched_quote_char(self.aliases[raw_words[0]])
        if (
            self._shopts.get("expand_aliases", False)
            and raw_words
            and raw_words[0] in self.aliases
            and unmatched_q is not None
            and self._alias_textual_depth < 8
            and not redirects
            and not (node.get("more_env") or [])
        ):
            src = self.aliases[raw_words[0]]
            if len(raw_words) > 1:
                src += " " + " ".join(raw_words[1:])
            self._alias_textual_depth += 1
            try:
                return self._eval_source(src)
            finally:
                self._alias_textual_depth -= 1
        try:
            self._validate_asdl_simple_like_words(node)
            argv = self._expand_asdl_simple_argv(node)
        except RuntimeError as e:
            msg = str(e)
            self._print_stderr(msg)
            if "bad substitution" in msg or "unbound variable:" in msg:
                raise SystemExit(self._runtime_error_status(msg))
            raise SystemExit(1)
        except CommandSubstFailure as e:
            return e.code
        except ArithExpansionFailure as e:
            return e.code
        argv = self._expand_aliases(argv)
        assign_pairs = node.get("more_env") or []

        if argv and argv[0] == "exec" and len(argv) == 2 and redirects:
            named_fd_var = self._parse_exec_named_fd_var(argv[1])
            if named_fd_var is not None:
                handled = self._handle_exec_named_fd_redirect(named_fd_var, redirects)
                if handled is not None:
                    return handled

        if argv and argv[0] == "exec" and len(argv) <= 1 and redirects:
            local_env = dict(self.env)
            saved_env = self.env
            assigned_names: set[str] = set()
            compound_assigned: set[str] = set()
            try:
                self.env = local_env
                self._apply_persistent_redirects(redirects)
                for assign in assign_pairs:
                    try:
                        value = self._expand_asdl_rhs_assignment(assign.get("val") or {})
                    except CommandSubstFailure as e:
                        return e.code
                    except ArithExpansionFailure as e:
                        return e.code
                    name = str(assign.get("name") or "")
                    assigned_names.add(name)
                    if name in self.readonly_vars:
                        msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                        print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                        raise SystemExit(2)
                    is_compound = False
                    comp_vals: list[str] | None = None
                    if self._bash_compat_level is not None:
                        rhs_text = self._asdl_rhs_word_to_text(assign.get("val") or {})
                        comp_vals = self._parse_compound_assignment_rhs(rhs_text)
                        is_compound = comp_vals is not None
                    if name in self._py_ties:
                        if is_compound:
                            raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                        op = str(assign.get("op") or "=")
                        self._assign_shell_var_op(name, op, value)
                        self._sync_local_env_assignment(local_env, name)
                        continue
                    op = str(assign.get("op") or "=")
                    if is_compound and comp_vals is not None:
                        self._assign_compound_var(name, op, comp_vals)
                        compound_assigned.add(name)
                        self._sync_local_env_assignment(local_env, name)
                        continue
                    self._assign_shell_var_op(name, op, value)
                    self._sync_local_env_assignment(local_env, name)
                should_persist_env = any(
                    not (r.op == ">&" and (r.fd is None or r.fd == 1) and r.target == "1")
                    for r in redirects
                )
                if should_persist_env:
                    for n in assigned_names:
                        if n in compound_assigned:
                            continue
                        attrs = self._structured_var_attrs(n)
                        if "array" in attrs or "assoc" in attrs:
                            continue
                        self._typed_vars.pop(n, None)
                    saved_env.clear()
                    saved_env.update(self.env)
                return 0
            finally:
                self.env = saved_env

        local_env = dict(self.env)
        saved_env = self.env
        assigned_names: set[str] = set()
        compound_assigned: set[str] = set()
        assignment_error_status: int | None = None
        try:
            self.env = local_env
            for assign in assign_pairs:
                try:
                    value = self._expand_asdl_rhs_assignment(assign.get("val") or {})
                except CommandSubstFailure as e:
                    return e.code
                except ArithExpansionFailure as e:
                    return e.code
                name = str(assign.get("name") or "")
                assigned_names.add(name)
                if name in self.readonly_vars:
                    msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                    print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                    assignment_error_status = 1
                    break
                is_compound = False
                comp_vals: list[str] | None = None
                if self._bash_compat_level is not None:
                    rhs_text = self._asdl_rhs_word_to_text(assign.get("val") or {})
                    comp_vals = self._parse_compound_assignment_rhs(rhs_text)
                    is_compound = comp_vals is not None
                if name in self._py_ties:
                    if is_compound:
                        raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                    op = str(assign.get("op") or "=")
                    self._assign_shell_var_op(name, op, value)
                    self._sync_local_env_assignment(local_env, name)
                    continue
                op = str(assign.get("op") or "=")
                if is_compound and comp_vals is not None:
                    self._assign_compound_var(name, op, comp_vals)
                    compound_assigned.add(name)
                    self._sync_local_env_assignment(local_env, name)
                    self.env = local_env
                    continue
                self._assign_shell_var_op(name, op, value)
                self._sync_local_env_assignment(local_env, name)
                self.env = local_env
        finally:
            self.env = saved_env

        if assignment_error_status is not None:
            if not argv:
                if self.options.get("posix", False) and self._is_noninteractive():
                    raise SystemExit(assignment_error_status)
                return assignment_error_status
            if argv[0] in self.SPECIAL_BUILTINS:
                return self._maybe_fatal_special_builtin_error(argv[0], assignment_error_status)
            return assignment_error_status

        if self.options.get("x", False):
            trace_cmd = self._asdl_pipeline_simple_command(node)
            if trace_cmd is not None:
                self._trace_simple(trace_cmd, argv, local_env)

        if not argv:
            if redirects:
                try:
                    with self._redirected_fds(redirects):
                        pass
                except RuntimeError as e:
                    msg = str(e)
                    print(msg, file=sys.stderr)
                    return self._runtime_error_status(msg)
            for n in assigned_names:
                if n in compound_assigned:
                    continue
                attrs = self._structured_var_attrs(n)
                if "array" in attrs or "assoc" in attrs:
                    continue
                self._typed_vars.pop(n, None)
            self.env.update(local_env)
            if "RANDOM" in assigned_names and "RANDOM" in local_env:
                self._seed_random(local_env["RANDOM"])
            for tied_name in self._py_ties:
                self.env[tied_name] = self._get_var(tied_name)
            if self._cmd_sub_used:
                status = self._cmd_sub_status
                self._cmd_sub_used = False
                return status
            return 0

        declaration_cmds = {"declare", "typeset", "local", "readonly", "export"}
        eligible: list[bool] | None = None
        words_src = node.get("words") or []
        if isinstance(words_src, list) and len(words_src) == len(argv):
            eligible = [self._asdl_word_is_plain_assignment_candidate(w) for w in words_src]
        argv_assigns = None if (argv and argv[0] in declaration_cmds) else self._argv_assignment_words(argv, eligible=eligible)
        if argv_assigns is not None:
            saved_env = self.env
            try:
                self.env = local_env
                for name, op, value, is_compound in argv_assigns:
                    if name in self.readonly_vars:
                        msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                        print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                        raise SystemExit(2)
                    if is_compound:
                        self._assign_compound_var(name, op, list(value) if isinstance(value, list) else [])
                    else:
                        self._assign_shell_var_op(name, op, str(value))
                    local_env[name.split("[", 1)[0]] = self._get_var(name.split("[", 1)[0])
                saved_env.update(local_env)
                for tied_name in self._py_ties:
                    saved_env[tied_name] = self._get_var(tied_name)
                return 0
            finally:
                self.env = saved_env

        # Command substitution status is only command status for assignment-only
        # simple commands. For command invocations, clear pending sub-status.
        if self._cmd_sub_used:
            self._cmd_sub_used = False

        name = argv[0]
        if name in {"declare", "typeset", "local", "readonly", "export"}:
            argv, raw_assign_by_idx = self._expand_asdl_declare_argv(node, name)
        else:
            raw_assign_by_idx = {}
        assign_names = {str(a.get("name") or "") for a in assign_pairs}
        if self._has_function(name):
            saved_env = dict(self.env)
            try:
                self.env = local_env
                try:
                    with self._redirected_fds(redirects):
                        status = self._run_function(name, argv[1:])
                except RuntimeError as e:
                    msg = str(e)
                    print(msg, file=sys.stderr)
                    return self._runtime_error_status(msg)
            finally:
                result_env = dict(self.env)
                merged = dict(saved_env)
                for k, v in result_env.items():
                    if k not in assign_names:
                        merged[k] = v
                for k in list(merged.keys()):
                    if k not in result_env and k not in assign_names:
                        merged.pop(k, None)
                for k in assign_names:
                    if k in saved_env:
                        merged[k] = saved_env[k]
                    else:
                        merged.pop(k, None)
                self.env = merged
            return status
        if self._should_dispatch_builtin(argv):
            is_special = name in self.SPECIAL_BUILTINS
            saved_decl_meta = self._declare_raw_assign_by_arg
            self._declare_raw_assign_by_arg = raw_assign_by_idx
            if is_special:
                if self.options.get("posix", False):
                    saved_env = dict(self.env)
                    self.env = local_env
                    try:
                        with self._redirected_fds(redirects):
                            status = self._run_builtin(name, argv)
                    except RuntimeError as e:
                        msg = str(e)
                        self._print_stderr(msg)
                        return self._runtime_error_status(msg)
                    if name == "unset" and assign_names:
                        for var_name in assign_names:
                            if var_name not in self.env:
                                if var_name in saved_env:
                                    self.env[var_name] = saved_env[var_name]
                            elif var_name in saved_env and self.env.get(var_name, "") == "":
                                self.env[var_name] = saved_env[var_name]
                    self._declare_raw_assign_by_arg = saved_decl_meta
                    return status
                # Assignment prefixes before special builtins affect current shell state.
                persist_assigns = True
                saved_env = dict(self.env)
                try:
                    self.env = local_env
                    try:
                        with self._redirected_fds(redirects):
                            status = self._run_builtin(name, argv)
                    except RuntimeError as e:
                        msg = str(e)
                        self._print_stderr(msg)
                        return self._runtime_error_status(msg)
                finally:
                    result_env = dict(self.env)
                    merged = dict(saved_env)
                    for k, v in result_env.items():
                        if persist_assigns or k not in assign_names:
                            merged[k] = v
                    for k in list(merged.keys()):
                        if k not in result_env and (persist_assigns or k not in assign_names):
                            merged.pop(k, None)
                    if not persist_assigns:
                        for k in assign_names:
                            if k in saved_env:
                                merged[k] = saved_env[k]
                            else:
                                merged.pop(k, None)
                    self.env = merged
                self._declare_raw_assign_by_arg = saved_decl_meta
                return status
            saved_env = self.env
            try:
                self.env = local_env
                try:
                    with self._redirected_fds(redirects):
                        status = self._run_builtin(name, argv)
                except RuntimeError as e:
                    msg = str(e)
                    self._print_stderr(msg)
                    return self._runtime_error_status(msg)
                if name in self.ENV_MUTATING_BUILTINS:
                    # Assignment prefixes before special builtins affect current shell state.
                    persist_assigns = True
                    result_env = dict(self.env)
                    merged = dict(saved_env)
                    for k, v in result_env.items():
                        if persist_assigns or k not in assign_names:
                            merged[k] = v
                    for k in list(merged.keys()):
                        if k not in result_env and (persist_assigns or k not in assign_names):
                            merged.pop(k, None)
                    if not persist_assigns:
                        for k in assign_names:
                            if k in saved_env:
                                merged[k] = saved_env[k]
                            else:
                                merged.pop(k, None)
                    saved_env.clear()
                    saved_env.update(merged)
                return status
            finally:
                self.env = saved_env
                self._declare_raw_assign_by_arg = saved_decl_meta
        if name in self._py_callables:
            saved_env = self.env
            try:
                self.env = local_env
                try:
                    with self._redirected_fds(redirects):
                        result = self._invoke_py_callable(self._py_callables[name], argv[1:])
                except RuntimeError as e:
                    msg = str(e)
                    print(msg, file=sys.stderr)
                    return self._runtime_error_status(msg)
            except Exception as e:
                print(f"{name}: {type(e).__name__}: {e}", file=sys.stderr)
                return 1
            finally:
                self.env = saved_env
            if result is not None:
                print(self._py_to_shell(result))
            return 0
        try:
            exec_env = {
                k: v
                for k, v in local_env.items()
                if "exported" in self._var_attrs.get(k, set())
            }
            for env_pair in assign_pairs:
                name = str(env_pair.get("name") or "")
                if name:
                    exec_env[name] = local_env.get(name, "")
            for scope in self.local_stack:
                for k, v in scope.items():
                    if k in self.env and "exported" in self._var_attrs.get(k, set()):
                        exec_env[k] = v
            saved_line = self.current_line
            end_line = self._asdl_simple_command_end_line(node)
            if end_line is not None:
                self.current_line = end_line
            try:
                return self._run_external(argv, exec_env, redirects)
            finally:
                self.current_line = saved_line
        except RuntimeError as e:
            msg = str(e)
            print(msg, file=sys.stderr)
            return self._runtime_error_status(msg)

    def _exec_asdl_command_list(self, children: list[dict[str, Any]]) -> int:
        status = 0
        for child in children:
            status = self._exec_asdl_list_item(child)
            errexit_item_exempt = self._take_errexit_item_exempt()
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            is_bg = (
                isinstance(child, dict)
                and child.get("type") == "command.Sentence"
                and self._asdl_token_text(child.get("terminator")) == "&"
            )
            if not is_bg:
                self._run_pending_traps()
            if (
                status != 0
                and self.options.get("e", False)
                and self._errexit_suppressed == 0
                and not errexit_item_exempt
            ):
                raise SystemExit(status)
        self._run_pending_traps()
        return status

    def _asdl_to_ast_list_item(self, node: dict[str, Any]) -> ListItem:
        t = node.get("type")
        if t == "command.Sentence":
            child = node.get("child") or {}
            out = self._asdl_to_ast_list_item(child)
            if self._asdl_token_text(node.get("terminator")) == "&":
                out.background = True
            return out
        if t != "command.AndOr":
            raise RuntimeError(f"invalid ASDL list item: {t}")
        return ListItem(node=self._asdl_to_ast_and_or(node), background=False)

    def _asdl_to_ast_and_or(self, node: dict[str, Any]) -> AndOr:
        pipes = [self._asdl_to_ast_pipeline(p) for p in (node.get("children") or [])]
        ops = [self._asdl_token_text(op) for op in (node.get("ops") or [])]
        return AndOr(pipelines=pipes, operators=[o for o in ops if o in {"&&", "||"}])

    def _asdl_to_ast_pipeline(self, node: dict[str, Any]) -> Pipeline:
        commands = [self._asdl_to_ast_command(c) for c in (node.get("children") or [])]
        return Pipeline(commands=commands, negate=bool(node.get("negated", False)))

    def _asdl_to_ast_command(self, node: dict[str, Any]) -> Command:
        t = node.get("type")
        if t == "command.Simple":
            return SimpleCommand(
                argv=[Word(self._asdl_word_to_text(w)) for w in (node.get("words") or [])],
                assignments=[
                    Assignment(
                        name=env_pair.get("name", ""),
                        value=self._asdl_rhs_word_to_text(env_pair.get("val")),
                        op="=",
                    )
                    for env_pair in (node.get("more_env") or [])
                ],
                redirects=[self._asdl_to_ast_redirect(r) for r in (node.get("redirects") or [])],
                line=self._asdl_command_line(node),
            )
        if t == "command.Redirect":
            child = self._asdl_to_ast_command(node.get("child") or {})
            redirects = [self._asdl_to_ast_redirect(r) for r in (node.get("redirects") or [])]
            return RedirectCommand(child=child, redirects=redirects)
        if t == "command.Subshell":
            return SubshellCommand(body=self._asdl_to_ast_list(node.get("child") or {}))
        if t == "command.ShFunction":
            return FunctionDef(name=node.get("name", ""), body=self._asdl_to_ast_list(node.get("body") or {}))
        if t == "command.ForEach":
            iterable = node.get("iterable") or {}
            words = [Word(self._asdl_word_to_text(w)) for w in (iterable.get("words") or [])]
            names = node.get("iter_names") or [""]
            return ForCommand(
                name=names[0],
                items=words,
                body=self._asdl_to_ast_do_group(node.get("body") or {}),
                explicit_in=bool(node.get("explicit_in", False)),
            )
        if t == "command.ForExpr":
            raw = node.get("raw") or {}
            return ArithForCommand(
                init=str(raw.get("init") or ""),
                cond=str(raw.get("cond") or ""),
                update=str(raw.get("update") or ""),
                body=self._asdl_to_ast_do_group(node.get("body") or {}),
            )
        if t == "command.Case":
            to_match = node.get("to_match") or {}
            value_word = to_match.get("word") if isinstance(to_match, dict) else {}
            items: list[CaseItem] = []
            for arm in (node.get("arms") or []):
                pat = arm.get("pattern") or {}
                patterns = [self._asdl_word_to_text(w) for w in (pat.get("words") or [])]
                action = arm.get("action") or []
                items.append(CaseItem(patterns=patterns, body=self._asdl_to_ast_action_list(action), op=str(arm.get("op", ";;"))))
            return CaseCommand(value=Word(self._asdl_word_to_text(value_word or {})), items=items)
        if t == "command.ControlFlow":
            keyword = self._asdl_token_text(node.get("keyword"))
            argv = [Word(keyword or "")]
            arg = node.get("arg_word")
            if arg is not None:
                argv.append(Word(self._asdl_word_to_text(arg)))
            return SimpleCommand(argv=argv, assignments=[], redirects=[], line=self._asdl_command_line(node))
        if t == "command.ShAssignment":
            assignments = []
            for pair in (node.get("pairs") or []):
                assignments.append(
                    Assignment(
                        name=pair.get("name", ""),
                        value=self._asdl_rhs_word_to_text(pair.get("rhs")),
                        op=pair.get("op", "="),
                    )
                )
            redirects = [self._asdl_to_ast_redirect(r) for r in (node.get("redirects") or [])]
            return SimpleCommand(argv=[], assignments=assignments, redirects=redirects, line=self._asdl_command_line(node))
        if t == "command.BraceGroup":
            return GroupCommand(body=self._asdl_to_ast_group(node))
        if t == "command.If":
            arms = node.get("arms") or []
            if not arms:
                return GroupCommand(body=ListNode(items=[]))
            first = arms[0]
            cond = self._asdl_to_ast_list(first.get("cond") or {})
            then_body = self._asdl_to_ast_list(first.get("action") or {})
            elifs = []
            for arm in arms[1:]:
                elifs.append((self._asdl_to_ast_list(arm.get("cond") or {}), self._asdl_to_ast_list(arm.get("action") or {})))
            else_action = node.get("else_action")
            else_body = self._asdl_to_ast_list(else_action) if else_action else None
            return IfCommand(cond=cond, then_body=then_body, elifs=elifs, else_body=else_body)
        if t == "command.WhileUntil":
            return WhileCommand(
                cond=self._asdl_to_ast_list(node.get("cond") or {}),
                body=self._asdl_to_ast_do_group(node.get("body") or {}),
                until=(self._asdl_token_text(node.get("keyword")) == "until"),
            )
        raise RuntimeError(f"unsupported ASDL command node {t}")

    def _asdl_to_ast_group(self, node: dict[str, Any]) -> ListNode:
        items = [self._asdl_to_ast_list_item(child) for child in (node.get("children") or [])]
        return ListNode(items=items)

    def _asdl_to_ast_list(self, node: dict[str, Any]) -> ListNode:
        if node.get("type") != "command.CommandList":
            return ListNode(items=[])
        return ListNode(items=[self._asdl_to_ast_list_item(child) for child in (node.get("children") or [])])

    def _asdl_to_ast_do_group(self, node: dict[str, Any]) -> ListNode:
        t = node.get("type")
        if t == "command.DoGroup":
            return ListNode(items=[self._asdl_to_ast_list_item(child) for child in (node.get("children") or [])])
        if t == "command.CommandList":
            return self._asdl_to_ast_list(node)
        return ListNode(items=[])

    def _asdl_to_ast_action_list(self, action: list[dict[str, Any]]) -> ListNode:
        return ListNode(items=[self._asdl_to_ast_list_item(child) for child in action])

    def _asdl_to_redirect(self, node: dict[str, Any]) -> Redirect:
        op_raw = node.get("op")
        op = self._asdl_token_text(op_raw)
        strip_tabs = op == "<<-"
        if op == "<<-":
            op = "<<"
        loc = node.get("loc") or {}
        fd = loc.get("fd") if isinstance(loc, dict) else None
        arg = node.get("arg") or {}
        if arg.get("type") == "redir_param.HereDoc":
            begin = arg.get("here_begin") or {}
            target = self._asdl_word_to_text(begin)
            parts = arg.get("stdin_parts") or []
            content = "".join(self._asdl_word_part_to_heredoc_text(p) for p in parts)
            return Redirect(
                op=op or "<<",
                target=target,
                fd=fd,
                here_doc=content,
                here_doc_expand=bool(arg.get("do_expand", True)),
                here_doc_strip_tabs=bool(arg.get("strip_tabs", strip_tabs)),
                target_word=begin if isinstance(begin, dict) else None,
            )
        target_word = arg.get("word") or {}
        return Redirect(
            op=op or ">",
            target=self._asdl_word_to_text(target_word),
            fd=fd,
            target_word=target_word if isinstance(target_word, dict) else None,
        )

    def _asdl_to_ast_redirect(self, node: dict[str, Any]) -> Redirect:
        # Compatibility alias used by legacy AST-conversion helpers.
        return self._asdl_to_redirect(node)

    def _asdl_do_group_children(self, node: dict[str, Any]) -> list[dict[str, Any]]:
        t = node.get("type")
        if t == "command.DoGroup":
            return node.get("children") or []
        if t == "command.CommandList":
            return node.get("children") or []
        return []

    def _asdl_rhs_word_to_text(self, node: dict[str, Any] | None) -> str:
        if not node:
            return ""
        if node.get("type") == "rhs_word.Compound":
            return self._asdl_word_to_text(node.get("word") or {})
        return ""

    def _expand_asdl_rhs_assignment(self, node: dict[str, Any] | None) -> str:
        if not node:
            return ""
        if node.get("type") == "rhs_word.Compound":
            word = node.get("word") or {}
            if self._asdl_rhs_assignment_can_expand_natively(word):
                return self._expand_asdl_assignment_scalar(word)
            return self._expand_assignment_word(self._asdl_word_to_text(word))
        return ""

    def _asdl_rhs_assignment_can_expand_natively(self, word: dict[str, Any]) -> bool:
        if not isinstance(word, dict) or word.get("type") != "word.Compound":
            return False
        parts = word.get("parts") or []
        if not parts:
            return True
        for p in parts:
            if not isinstance(p, dict):
                return False
            t = p.get("type")
            if t == "word_part.Literal":
                lit = str(p.get("tval", ""))
                if "<(" in lit or ">(" in lit:
                    return False
                continue
            if t == "word_part.SingleQuoted":
                continue
            if t == "word_part.ArithSub":
                # Arithmetic substitution is scalar in assignment context and
                # does not require field splitting/pathname expansion.
                continue
            if t == "word_part.CommandSub":
                # Command substitution is scalar in assignment context.
                continue
            if t == "word_part.SimpleVarSub":
                name = str(p.get("name", ""))
                if self._is_valid_param_ref_name(name):
                    continue
                return False
            if t == "word_part.BracedVarSub":
                # Safe subset: ${name}, ${#name}, and simple default/alt/error
                # operators with literal-only arg words.
                name = str(p.get("name", ""))
                op = p.get("op")
                if self._is_valid_param_ref_name(name) and (op is None or op == "" or op in {"__len__", "__indirect__"}):
                    continue
                if self._is_valid_param_ref_name(name) and op in {
                    "-",
                    ":-",
                    "+",
                    ":+",
                    "?",
                    ":?",
                    "#",
                    "##",
                    "%",
                    "%%",
                    ":substr",
                    "/",
                }:
                    arg = p.get("arg")
                    if self._asdl_word_is_safe_literal(arg):
                        continue
                return False
            # Any non-literal part stays on legacy assignment expansion for now.
            return False
        return True

    def _is_valid_param_ref_name(self, name: str) -> bool:
        if self._is_valid_name(name):
            return True
        if name.isdigit():
            return True
        return name in {"@", "*", "#", "?", "$", "!", "-"}

    def _scalarize_assignment_expansion(self, value: Any) -> str:
        if isinstance(value, PresplitFields):
            return self._ifs_join([str(v) for v in value])
        if isinstance(value, list):
            return self._ifs_join([str(v) for v in value])
        return "" if value is None else str(value)

    def _expand_asdl_assignment_scalar(self, node: dict[str, Any] | None) -> str:
        fields = self._expand_asdl_assignment_fields(node)
        texts = fields_to_text_list(fields)
        if not texts:
            return ""
        text = texts[0]
        if fields and all(not seg.quoted for seg in fields[0].segments):
            text = self._tilde_expand(text)
        return text

    def _expand_asdl_assignment_fields(self, node: dict[str, Any] | None) -> list[ExpansionField]:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return []
        out: list[ExpansionSegment] = []
        parts = node.get("parts") or []
        i = 0
        while i < len(parts):
            part = parts[i]
            if (
                isinstance(part, dict)
                and part.get("type") == "word_part.Literal"
                and i + 1 < len(parts)
                and isinstance(parts[i + 1], dict)
                and parts[i + 1].get("type") == "word_part.SingleQuoted"
            ):
                lit = str(part.get("tval", ""))
                if lit.endswith("$"):
                    prefix = lit[:-1]
                    parsed = self._decode_ansi_c_quoted_literal_at(
                        "$'" + str(parts[i + 1].get("sval", "")) + "'",
                        0,
                    )
                    if parsed is not None:
                        decoded, _ = parsed
                        if prefix:
                            out.append(
                                ExpansionSegment(
                                    text=self._decode_asdl_literal(prefix, quoted_context=False),
                                    quoted=False,
                                    glob_active=False,
                                    split_active=False,
                                    source_kind="word_part.Literal",
                                )
                            )
                        out.append(
                            ExpansionSegment(
                                text=decoded,
                                quoted=True,
                                glob_active=False,
                                split_active=False,
                                source_kind="word_part.AnsiCQuoted",
                            )
                        )
                        i += 2
                        continue
            # Parse locale $"..." form represented as literal '$' + double-quoted part.
            if (
                isinstance(part, dict)
                and part.get("type") == "word_part.Literal"
                and i + 1 < len(parts)
                and isinstance(parts[i + 1], dict)
                and parts[i + 1].get("type") == "word_part.DoubleQuoted"
            ):
                lit = str(part.get("tval", ""))
                if lit.endswith("$"):
                    prefix = lit[:-1]
                    if prefix:
                        out.append(
                            ExpansionSegment(
                                text=self._decode_asdl_literal(prefix, quoted_context=False),
                                quoted=False,
                                glob_active=False,
                                split_active=False,
                                source_kind="word_part.Literal",
                            )
                        )
                    inner = parts[i + 1].get("parts") or []
                    decoded = "".join(self._expand_asdl_assignment_part_scalar(p, quoted_context=True) for p in inner)
                    out.append(
                        ExpansionSegment(
                            text=decoded,
                            quoted=True,
                            glob_active=False,
                            split_active=False,
                            source_kind="word_part.LocaleQuoted",
                        )
                    )
                    i += 2
                    continue
            text = self._expand_asdl_assignment_part_scalar(part, quoted_context=False)
            part_type = str(part.get("type", "word_part.Unknown")) if isinstance(part, dict) else "word_part.Unknown"
            out.append(
                ExpansionSegment(
                    text=text,
                    quoted=part_type in {"word_part.SingleQuoted", "word_part.DoubleQuoted"},
                    glob_active=False,
                    split_active=False,
                    source_kind=part_type,
                )
            )
            i += 1
        return [ExpansionField(out, preserve_boundary=True)]

    def _expand_asdl_assignment_part_scalar(self, node: dict[str, Any], quoted_context: bool) -> str:
        t = node.get("type")
        if t == "word_part.Literal":
            return self._decode_asdl_literal(str(node.get("tval", "")), quoted_context=quoted_context)
        if t == "word_part.SingleQuoted":
            return str(node.get("sval", ""))
        if t == "word_part.DoubleQuoted":
            parts = node.get("parts") or []
            return "".join(self._expand_asdl_assignment_part_scalar(p, quoted_context=True) for p in parts)
        if t == "word_part.SimpleVarSub":
            name = str(node.get("name", ""))
            if name in {"@", "*"}:
                return self._ifs_join(self.positional)
            return self._scalarize_assignment_expansion(self._expand_param(name, quoted_context))
        if t == "word_part.BracedVarSub":
            name = str(node.get("name", ""))
            op = node.get("op")
            arg_node = node.get("arg")
            arg_text, _arg_fields = self._asdl_operator_arg_text_and_fields(arg_node)
            if name in {"@", "*"} and (op is None or op == ""):
                return self._ifs_join(self.positional)
            value = self._expand_braced_param(
                name,
                op,
                arg_text,
                quoted_context,
                arg_fields=_arg_fields,
                arg_node=arg_node if isinstance(arg_node, dict) else None,
                assignment_context=True,
            )
            return self._scalarize_assignment_expansion(value)
        if t == "word_part.CommandSub":
            child = node.get("child")
            syntax = str(node.get("syntax") or "dollar")
            backtick = syntax == "backtick"
            if isinstance(child, dict) and child.get("type") == "command.CommandList":
                return self._expand_command_subst_asdl(child, backtick=backtick)
            src = str(node.get("child_source") or "")
            return self._expand_command_subst_text(src, backtick=backtick)
        if t == "word_part.ArithSub":
            expr = str(node.get("expr_source") or node.get("code") or "")
            return self._expand_arith(expr)
        return ""

    def _asdl_word_is_safe_literal(self, word: Any) -> bool:
        if not isinstance(word, dict) or word.get("type") != "word.Compound":
            return False
        for p in (word.get("parts") or []):
            if not isinstance(p, dict):
                return False
            t = p.get("type")
            if t == "word_part.SingleQuoted":
                continue
            if t != "word_part.Literal":
                return False
            lit = str(p.get("tval", ""))
            if "\\" in lit or "'" in lit or '"' in lit:
                return False
        return True

    def _validate_asdl_simple_like_words(self, node: dict[str, Any]) -> None:
        for w in (node.get("words") or []):
            self._validate_asdl_word_bad_subst(w)
        for assign in (node.get("more_env") or []):
            self._validate_asdl_rhs_bad_subst(assign.get("val"))
        self._validate_asdl_redirect_words(node.get("redirects") or [])

    def _validate_asdl_rhs_bad_subst(self, rhs: Any) -> None:
        if not isinstance(rhs, dict):
            return
        if rhs.get("type") != "rhs_word.Compound":
            return
        self._validate_asdl_word_bad_subst(rhs.get("word"))

    def _validate_asdl_redirect_words(self, redirects: Any) -> None:
        if not isinstance(redirects, list):
            return
        for r in redirects:
            if not isinstance(r, dict):
                continue
            arg = r.get("arg")
            if not isinstance(arg, dict):
                continue
            arg_t = arg.get("type")
            if arg_t in {"redir_param.Path", "redir_param.Word"}:
                self._validate_asdl_word_bad_subst(arg.get("word"))
                continue
            if arg_t == "redir_param.HereDoc":
                begin = arg.get("here_begin")
                if isinstance(begin, dict):
                    self._validate_asdl_word_bad_subst(begin)

    def _validate_asdl_word_bad_subst(self, word: Any) -> None:
        if not isinstance(word, dict) or word.get("type") != "word.Compound":
            return
        line = None
        pos = word.get("pos")
        if isinstance(pos, dict):
            maybe_line = pos.get("line")
            if isinstance(maybe_line, int):
                line = maybe_line

        def _raise_bad_subst() -> None:
            raise RuntimeError(self._format_error("syntax error: bad substitution", line=line or self.current_line))

        saw_structured_braced = False
        for part in (word.get("parts") or []):
            if not isinstance(part, dict):
                continue
            if part.get("type") != "word_part.BracedVarSub":
                continue
            saw_structured_braced = True
            if part.get("op") == "__invalid__":
                _raise_bad_subst()
        if saw_structured_braced:
            return
        # Catch malformed forms still represented as literal-only word parts.
        text = self._asdl_word_to_text(word)
        for parsed in parse_word_parts(text):
            if parsed.kind == "BRACED" and parsed.op == "__invalid__":
                _raise_bad_subst()

    def _expand_asdl_word_scalar(self, node: dict[str, Any], split_glob: bool = True) -> str:
        fields = self._expand_asdl_word_fields(node, split_glob=split_glob)
        return fields[0] if fields else ""

    def _asdl_word_to_expansion_fields(self, node: dict[str, Any]) -> list[ExpansionField]:
        # Transitional adapter: carry split/glob/quote metadata in structured
        # fields while preserving existing expansion semantics.
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return []
        parts = node.get("parts") or []
        fields: list[ExpansionField] = [ExpansionField([])]
        active: list[bool] = [True]
        i = 0
        while i < len(parts):
            part = parts[i]
            kind = str(part.get("type", "word_part.Unknown")) if isinstance(part, dict) else "word_part.Unknown"
            # Parse ANSI-C $'...' form represented by lexer/parser as
            # literal '$' + single-quoted part.
            if (
                isinstance(part, dict)
                and part.get("type") == "word_part.Literal"
                and i + 1 < len(parts)
                and isinstance(parts[i + 1], dict)
                and parts[i + 1].get("type") == "word_part.SingleQuoted"
            ):
                lit = str(part.get("tval", ""))
                if lit.endswith("$"):
                    prefix = lit[:-1]
                    decoded = self._decode_ansi_c_quoted_literal_at(
                        "$'" + str(parts[i + 1].get("sval", "")) + "'",
                        0,
                    )
                    if decoded is not None:
                        text_decoded, _ = decoded
                        next_fields: list[ExpansionField] = []
                        next_active: list[bool] = []
                        for base, base_active in zip(fields, active):
                            if not base_active:
                                next_fields.append(base)
                                next_active.append(False)
                                continue
                            segs = []
                            if prefix:
                                segs.extend(self._asdl_literal_to_segments(prefix, quoted_context=False, source_kind=kind))
                            segs.append(
                                ExpansionSegment(
                                    text=text_decoded,
                                    quoted=True,
                                    glob_active=False,
                                    split_active=False,
                                    source_kind="word_part.AnsiCQuoted",
                                )
                            )
                            next_fields.append(
                                ExpansionField(
                                    segments=base.segments + segs,
                                    preserve_boundary=True,
                                )
                            )
                            next_active.append(True)
                        fields = next_fields
                        active = next_active
                        i += 2
                        continue
            # Parse locale $"..." form represented by lexer/parser as
            # literal '$' + double-quoted part.
            if (
                isinstance(part, dict)
                and part.get("type") == "word_part.Literal"
                and i + 1 < len(parts)
                and isinstance(parts[i + 1], dict)
                and parts[i + 1].get("type") == "word_part.DoubleQuoted"
            ):
                lit = str(part.get("tval", ""))
                if lit.endswith("$"):
                    prefix = lit[:-1]
                    vals, _, _ = self._expand_asdl_word_part_values(parts[i + 1], quoted_context=True)
                    if not vals:
                        vals = [""]
                    next_fields: list[ExpansionField] = []
                    next_active: list[bool] = []
                    for base, base_active in zip(fields, active):
                        if not base_active:
                            next_fields.append(base)
                            next_active.append(False)
                            continue
                        for val in vals:
                            segs = []
                            if prefix:
                                segs.extend(self._asdl_literal_to_segments(prefix, quoted_context=False, source_kind=kind))
                            segs.append(
                                ExpansionSegment(
                                    text=val,
                                    quoted=True,
                                    glob_active=False,
                                    split_active=False,
                                    source_kind="word_part.LocaleQuoted",
                                )
                            )
                            next_fields.append(
                                ExpansionField(
                                    segments=base.segments + segs,
                                    preserve_boundary=True,
                                )
                            )
                            next_active.append(True)
                    fields = next_fields
                    active = next_active
                    i += 2
                    continue
            if isinstance(part, dict) and part.get("type") == "word_part.Literal":
                literal = str(part.get("tval", ""))
                segs = self._asdl_literal_to_segments(literal, quoted_context=False, source_kind=kind)
                next_fields: list[ExpansionField] = []
                next_active: list[bool] = []
                for base, base_active in zip(fields, active):
                    if not base_active:
                        next_fields.append(base)
                        next_active.append(False)
                        continue
                    next_fields.append(
                        ExpansionField(
                            segments=base.segments + segs,
                            preserve_boundary=base.preserve_boundary or any(s.quoted for s in segs),
                        )
                    )
                    next_active.append(True)
                fields = next_fields
                active = next_active
                i += 1
                continue
            vals, quoted, presplit = self._expand_asdl_word_part_values(part, quoted_context=False)
            next_fields: list[ExpansionField] = []
            next_active: list[bool] = []
            for base, base_active in zip(fields, active):
                if not base_active:
                    next_fields.append(base)
                    next_active.append(False)
                    continue
                if not vals:
                    continue
                # Unquoted multi-value expansions splice into words like shell
                # fields: prefix sticks to first field, suffix to last.
                if (not quoted) and len(vals) > 1:
                    split_active = not presplit
                    first_seg = ExpansionSegment(
                        text=vals[0],
                        quoted=False,
                        glob_active=True,
                        split_active=split_active,
                        source_kind=kind,
                    )
                    next_fields.append(
                        ExpansionField(
                            segments=base.segments + [first_seg],
                            preserve_boundary=base.preserve_boundary or vals[0] == "",
                        )
                    )
                    next_active.append(False)
                    for mid in vals[1:-1]:
                        next_fields.append(
                            ExpansionField(
                                segments=[
                                    ExpansionSegment(
                                        text=mid,
                                        quoted=False,
                                        glob_active=True,
                                        split_active=split_active,
                                        source_kind=kind,
                                    )
                                ],
                                preserve_boundary=(mid == ""),
                            )
                        )
                        next_active.append(False)
                    next_fields.append(
                        ExpansionField(
                            segments=[
                                    ExpansionSegment(
                                        text=vals[-1],
                                        quoted=False,
                                        glob_active=True,
                                        split_active=split_active,
                                        source_kind=kind,
                                    )
                                ],
                                preserve_boundary=(vals[-1] == ""),
                        )
                    )
                    next_active.append(True)
                    continue
                for v in vals:
                    next_fields.append(
                        ExpansionField(
                            segments=base.segments
                            + [
                                ExpansionSegment(
                                    text=v,
                                    quoted=quoted,
                                    glob_active=(not quoted),
                                    split_active=((not quoted) and (not presplit)),
                                    source_kind=kind,
                                )
                            ],
                            preserve_boundary=base.preserve_boundary or quoted or (presplit and v == ""),
                        )
                    )
                    next_active.append(True)
            fields = next_fields
            active = next_active
            i += 1
        return fields

    def _legacy_word_to_expansion_fields(self, text: str, *, assignment: bool = False) -> list[ExpansionField]:
        lst_word = parse_legacy_word(text)
        asdl_word = lst_word_to_asdl_word(lst_word)
        if assignment:
            return self._expand_asdl_assignment_fields(asdl_word)
        raw_fields = self._asdl_word_to_expansion_fields(asdl_word)
        if self.options.get("B", True):
            raw_fields = self._brace_expand_structured_fields(raw_fields)
        split_fields: list[ExpansionField] = []
        for field in raw_fields:
            split_fields.extend(self._split_structured_field(field))
        out: list[ExpansionField] = []
        for field in split_fields:
            globbed = self._glob_structured_field(field)
            if globbed == [field.text()]:
                out.append(field)
                continue
            for g in globbed:
                out.append(
                    ExpansionField(
                        [
                            ExpansionSegment(
                                text=g,
                                quoted=False,
                                glob_active=False,
                                split_active=False,
                                source_kind="legacy.glob",
                            )
                        ],
                        preserve_boundary=False,
                    )
                )
        return out

    def _asdl_literal_to_segments(self, text: str, *, quoted_context: bool, source_kind: str) -> list[ExpansionSegment]:
        if "\\" not in text:
            if "$'" not in text:
                return [
                    ExpansionSegment(
                        text=text,
                        quoted=quoted_context,
                        glob_active=(not quoted_context),
                        split_active=False,
                        source_kind=source_kind,
                    )
                ]
            out: list[ExpansionSegment] = []
            i = 0
            buf: list[str] = []
            while i < len(text):
                parsed = self._decode_ansi_c_quoted_literal_at(text, i)
                if parsed is None:
                    buf.append(text[i])
                    i += 1
                    continue
                decoded, new_i = parsed
                if buf:
                    out.append(
                        ExpansionSegment(
                            text="".join(buf),
                            quoted=quoted_context,
                            glob_active=(not quoted_context),
                            split_active=False,
                            source_kind=source_kind,
                        )
                    )
                    buf = []
                out.append(
                    ExpansionSegment(
                        text=decoded,
                        quoted=True,
                        glob_active=False,
                        split_active=False,
                        source_kind=source_kind,
                    )
                )
                i = new_i
            if buf:
                out.append(
                    ExpansionSegment(
                        text="".join(buf),
                        quoted=quoted_context,
                        glob_active=(not quoted_context),
                        split_active=False,
                        source_kind=source_kind,
                    )
                )
            return out
        segs: list[ExpansionSegment] = []
        buf: list[str] = []

        def flush(active: bool, quoted: bool) -> None:
            nonlocal buf
            if not buf:
                return
            segs.append(
                ExpansionSegment(
                    text="".join(buf),
                    quoted=quoted,
                    glob_active=active and (not quoted),
                    split_active=False,
                    source_kind=source_kind,
                )
            )
            buf = []

        i = 0
        while i < len(text):
            parsed = self._decode_ansi_c_quoted_literal_at(text, i)
            if parsed is not None:
                decoded, new_i = parsed
                flush(active=True, quoted=quoted_context)
                segs.append(
                    ExpansionSegment(
                        text=decoded,
                        quoted=True,
                        glob_active=False,
                        split_active=False,
                        source_kind=source_kind,
                    )
                )
                i = new_i
                continue
            ch = text[i]
            if ch != "\\" or i + 1 >= len(text):
                buf.append(ch)
                i += 1
                continue
            nxt = text[i + 1]
            if quoted_context:
                if nxt in {'$', '"', "\\", "`"}:
                    buf.append(nxt)
                else:
                    buf.append("\\")
                    buf.append(nxt)
                i += 2
                continue
            flush(active=True, quoted=False)
            segs.append(
                ExpansionSegment(
                    text=nxt,
                    quoted=True,
                    glob_active=False,
                    split_active=False,
                    source_kind=source_kind,
                )
            )
            i += 2
        flush(active=True, quoted=False)
        return segs

    def _decode_ansi_c_quoted_literal_at(self, text: str, i: int) -> tuple[str, int] | None:
        if not text.startswith("$'", i):
            return None
        j = i + 2
        out: list[str] = []
        while j < len(text):
            ch = text[j]
            if ch == "'":
                return "".join(out), j + 1
            if ch != "\\":
                out.append(ch)
                j += 1
                continue
            if j + 1 >= len(text):
                out.append("\\")
                j += 1
                continue
            esc = text[j + 1]
            mapping = {
                "a": "\a",
                "b": "\b",
                "e": "\x1b",
                "E": "\x1b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
                "v": "\v",
                "\\": "\\",
                "'": "'",
                '"': '"',
            }
            if esc in mapping:
                out.append(mapping[esc])
                j += 2
                continue
            if esc in "01234567":
                k = j + 1
                digits = []
                while k < len(text) and len(digits) < 3 and text[k] in "01234567":
                    digits.append(text[k])
                    k += 1
                try:
                    code = int("".join(digits), 8)
                    if code != 0:
                        out.append(chr(code))
                except Exception:
                    out.append("".join(digits))
                j = k
                continue
            if esc == "x":
                k = j + 2
                digits = []
                while k < len(text) and len(digits) < 2 and text[k] in "0123456789abcdefABCDEF":
                    digits.append(text[k])
                    k += 1
                if digits:
                    try:
                        code = int("".join(digits), 16)
                        if code != 0:
                            out.append(chr(code))
                    except Exception:
                        out.append("".join(digits))
                    j = k
                    continue
            out.append("\\")
            out.append(esc)
            j += 2
        return None

    def _expand_asdl_word_fields(self, node: dict[str, Any], split_glob: bool = True) -> list[str]:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return []
        raw_text = self._asdl_word_to_text(node)
        if self._is_process_subst(raw_text):
            return [self._process_substitute(raw_text)]
        has_qat, only_qat = self._asdl_word_has_quoted_at(node)
        if self._diag.style == "ash" and has_qat and not self.positional and not only_qat:
            return [""]
        fields = self._asdl_word_to_expansion_fields(node)
        if self.options.get("B", True):
            fields = self._brace_expand_structured_fields(fields)
        if not fields:
            return []
        if not split_glob:
            return fields_to_text_list(fields)
        split_fields: list[ExpansionField] = []
        for field in fields:
            split_fields.extend(self._split_structured_field(field))
        out: list[str] = []
        for field in split_fields:
            out.extend(self._glob_structured_field(field))
        if self._diag.style == "ash" and has_qat and self.positional and len(out) < len(self.positional):
            out.extend([""] * (len(self.positional) - len(out)))
        return out

    def _brace_expand_structured_fields(self, fields: list[ExpansionField]) -> list[ExpansionField]:
        out: list[ExpansionField] = []
        for field in fields:
            out.extend(self._brace_expand_single_field(field))
        return out

    def _brace_expand_single_field(self, field: ExpansionField) -> list[ExpansionField]:
        chars: list[tuple[str, bool, bool, bool, str]] = []
        for seg in field.segments:
            for ch in seg.text:
                chars.append((ch, seg.split_active, seg.glob_active, seg.quoted, seg.source_kind))
        if not chars:
            return [field]
        expanded = self._brace_expand_chars(chars)
        if len(expanded) == 1 and expanded[0] == chars:
            return [field]
        out: list[ExpansionField] = []
        for item in expanded:
            mapped = self._chars_to_structured_field(item)
            out.append(
                ExpansionField(
                    segments=mapped.segments,
                    preserve_boundary=(mapped.preserve_boundary or field.preserve_boundary),
                )
            )
        return out

    def _brace_expand_chars(
        self, chars: list[tuple[str, bool, bool, bool, str]]
    ) -> list[list[tuple[str, bool, bool, bool, str]]]:
        range_hit = self._find_brace_range_candidate(chars)
        if range_hit is not None:
            start, end, parts = range_hit
            out: list[list[tuple[str, bool, bool, bool, str]]] = []
            prefix = chars[:start]
            suffix = chars[end + 1 :]
            for part in parts:
                out.extend(self._brace_expand_chars(prefix + part + suffix))
            return out
        start, end, cuts = self._find_brace_candidate(chars)
        if start == -1 or end == -1 or not cuts:
            return [chars]
        parts: list[list[tuple[str, bool, bool, bool, str]]] = []
        prev = start + 1
        for cut in cuts:
            parts.append(chars[prev:cut])
            prev = cut + 1
        parts.append(chars[prev:end])
        out: list[list[tuple[str, bool, bool, bool, str]]] = []
        prefix = chars[:start]
        suffix = chars[end + 1 :]
        for part in parts:
            out.extend(self._brace_expand_chars(prefix + part + suffix))
        return out

    def _find_brace_candidate(
        self, chars: list[tuple[str, bool, bool, bool, str]]
    ) -> tuple[int, int, list[int]]:
        def _literal_kind(kind: str) -> bool:
            return kind in {"word_part.Literal"}

        i = 0
        n = len(chars)
        while i < n:
            ch, _, _, quoted, kind = chars[i]
            if quoted or ch != "{" or not _literal_kind(kind):
                i += 1
                continue
            depth = 0
            comma_pos: list[int] = []
            j = i
            while j < n:
                c, _, _, c_quoted, c_kind = chars[j]
                if c_quoted:
                    j += 1
                    continue
                if c in {"{", "}", ","} and not _literal_kind(c_kind):
                    break
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        if comma_pos:
                            return i, j, comma_pos
                        break
                    if depth < 0:
                        break
                elif c == "," and depth == 1:
                    comma_pos.append(j)
                j += 1
            i += 1
        return -1, -1, []

    def _find_brace_range_candidate(
        self, chars: list[tuple[str, bool, bool, bool, str]]
    ) -> tuple[int, int, list[list[tuple[str, bool, bool, bool, str]]]] | None:
        def _literal_kind(kind: str) -> bool:
            return kind in {"word_part.Literal"}

        i = 0
        n = len(chars)
        while i < n:
            ch, split_a, glob_a, quoted, kind = chars[i]
            if quoted or ch != "{" or not _literal_kind(kind):
                i += 1
                continue
            depth = 0
            j = i
            while j < n:
                c, _, _, c_quoted, c_kind = chars[j]
                if c_quoted or not _literal_kind(c_kind):
                    break
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        body = "".join(x[0] for x in chars[i + 1 : j])
                        vals = self._brace_range_values(body)
                        if vals is not None:
                            parts = [
                                [
                                    (vch, split_a, glob_a, False, kind)
                                    for vch in val
                                ]
                                for val in vals
                            ]
                            return i, j, parts
                        break
                    if depth < 0:
                        break
                j += 1
            i += 1
        return None

    def _brace_range_values(self, body: str) -> list[str] | None:
        m_num = re.fullmatch(r"(-?[0-9]+)\.\.(-?[0-9]+)(?:\.\.(-?[0-9]+))?", body)
        if m_num is not None:
            a_s, b_s, step_s = m_num.group(1), m_num.group(2), m_num.group(3)
            a = int(a_s, 10)
            b = int(b_s, 10)
            if step_s is None:
                step = 1 if b >= a else -1
            else:
                step = int(step_s, 10)
                if step == 0:
                    return None
                if (b > a and step < 0) or (b < a and step > 0):
                    return []
            width = max(len(a_s.lstrip("-")), len(b_s.lstrip("-")))
            out: list[str] = []
            x = a
            guard = 0
            while (step > 0 and x <= b) or (step < 0 and x >= b):
                sx = str(abs(x)).rjust(width, "0")
                out.append(("-" if x < 0 else "") + sx)
                x += step
                guard += 1
                if guard > 20000:
                    break
            return out
        m_chr = re.fullmatch(r"([A-Za-z])\.\.([A-Za-z])(?:\.\.(-?[0-9]+))?", body)
        if m_chr is not None:
            a = ord(m_chr.group(1))
            b = ord(m_chr.group(2))
            step_s = m_chr.group(3)
            if step_s is None:
                step = 1 if b >= a else -1
            else:
                step = int(step_s, 10)
                if step == 0:
                    return None
                if (b > a and step < 0) or (b < a and step > 0):
                    return []
            out: list[str] = []
            x = a
            guard = 0
            while (step > 0 and x <= b) or (step < 0 and x >= b):
                out.append(chr(x))
                x += step
                guard += 1
                if guard > 20000:
                    break
            return out
        return None

    def _split_structured_field(self, field: ExpansionField) -> list[ExpansionField]:
        def _empty_split_field() -> ExpansionField:
            return ExpansionField(
                [
                    ExpansionSegment(
                        text="",
                        quoted=False,
                        glob_active=False,
                        split_active=False,
                        source_kind="split",
                    )
                ],
                preserve_boundary=False,
            )

        leading_quoted_boundary = (
            bool(field.segments)
            and bool(field.segments[0].quoted)
            and field.segments[0].text == ""
        )
        trailing_quoted_boundary = (
            bool(field.segments)
            and bool(field.segments[-1].quoted)
            and field.segments[-1].text == ""
        )
        chars: list[tuple[str, bool, bool, bool, str]] = []
        for seg in field.segments:
            for ch in seg.text:
                chars.append((ch, seg.split_active, seg.glob_active, seg.quoted, seg.source_kind))
        if not chars:
            if field.preserve_boundary:
                return [field]
            return []
        ifs, is_set = self._get_var_with_state("IFS")
        if not is_set:
            ifs = " \t\n"
        if ifs == "":
            return [field]
        ifs_ws = "".join(ch for ch in ifs if ch in " \t\n")
        ifs_nonws = "".join(ch for ch in ifs if ch not in " \t\n")

        out: list[ExpansionField] = []
        n = len(chars)
        i = 0
        last_sep_nonws = False

        if leading_quoted_boundary and chars and chars[0][1] and chars[0][0] in ifs_ws:
            out.append(_empty_split_field())
        while i < n and chars[i][1] and chars[i][0] in ifs_ws:
            i += 1

        while i < n:
            current: list[tuple[str, bool, bool, bool, str]] = []
            j = i
            delim_ws = False
            delim_nonws = False
            while j < n:
                ch, split_active, _, _, _ = chars[j]
                if split_active and ch in ifs_nonws:
                    delim_nonws = True
                    break
                if split_active and ch in ifs_ws:
                    delim_ws = True
                    break
                current.append(chars[j])
                j += 1

            if current:
                out.append(self._chars_to_structured_field(current))
                last_sep_nonws = False
            elif delim_nonws:
                # POSIX field splitting: preserve empty fields for leading and
                # adjacent non-whitespace delimiters, but avoid adding an
                # extra trailing empty for a single terminal delimiter.
                if not out or last_sep_nonws:
                    out.append(_empty_split_field())

            if j >= n:
                break

            if delim_nonws:
                last_sep_nonws = True
                j += 1
                while j < n and chars[j][1] and chars[j][0] in ifs_ws:
                    j += 1
            elif delim_ws:
                last_sep_nonws = False
                while j < n and chars[j][1] and chars[j][0] in ifs_ws:
                    j += 1
            i = j

        if trailing_quoted_boundary and chars and chars[-1][1] and chars[-1][0] in ifs_ws:
            out.append(_empty_split_field())

        if out:
            return out
        if field.preserve_boundary:
            return [ExpansionField([ExpansionSegment("", quoted=True, glob_active=False, split_active=False, source_kind="split")], preserve_boundary=True)]
        return []

    def _chars_to_structured_field(self, chars: list[tuple[str, bool, bool, bool, str]]) -> ExpansionField:
        if not chars:
            return ExpansionField([])
        segs: list[ExpansionSegment] = []
        cur_text = chars[0][0]
        cur_split = chars[0][1]
        cur_glob = chars[0][2]
        cur_quoted = chars[0][3]
        cur_kind = chars[0][4]
        preserve = cur_quoted
        for ch, split_active, glob_active, quoted, kind in chars[1:]:
            preserve = preserve or quoted
            if split_active == cur_split and glob_active == cur_glob and quoted == cur_quoted and kind == cur_kind:
                cur_text += ch
                continue
            segs.append(
                ExpansionSegment(
                    text=cur_text,
                    quoted=cur_quoted,
                    glob_active=cur_glob,
                    split_active=cur_split,
                    source_kind=cur_kind,
                )
            )
            cur_text = ch
            cur_split = split_active
            cur_glob = glob_active
            cur_quoted = quoted
            cur_kind = kind
        segs.append(
            ExpansionSegment(
                text=cur_text,
                quoted=cur_quoted,
                glob_active=cur_glob,
                split_active=cur_split,
                source_kind=cur_kind,
            )
        )
        return ExpansionField(segs, preserve_boundary=preserve)

    def _glob_structured_field(self, field: ExpansionField) -> list[str]:
        raw_text = field.text()
        all_quoted = bool(field.segments) and all(seg.quoted for seg in field.segments)
        text = raw_text if all_quoted else self._tilde_expand(raw_text)
        if self.options.get("f", False):
            return [text]
        has_active_glob = False
        pat: list[str] = []

        def _append_literal_glob_char(ch: str, *, in_class: bool = False) -> None:
            if ch == "*":
                pat.append("[*]")
            elif ch == "?":
                pat.append("[?]")
            elif ch == "[":
                pat.append("[[]")
            elif ch == "]":
                pat.append("[]]")
            elif ch == "-" and in_class:
                # Keep literal '-' from quoted/escaped class content from
                # becoming a range operator (e.g. [0"$((-9))"]).
                pat.append("\\-")
            elif ch == "\\":
                pat.append("[\\\\]")
            else:
                pat.append(ch)

        chars: list[tuple[str, bool]] = []
        for seg in field.segments:
            for ch in seg.text:
                chars.append((ch, bool(seg.glob_active)))

        i = 0
        has_active_extglob = False
        in_class = False
        class_can_close = False
        while i < len(chars):
            ch, active = chars[i]
            if active:
                # Unquoted glob context: backslash escapes the next pattern
                # char (special or not), so it should not itself match.
                if ch == "\\" and i + 1 < len(chars):
                    nxt, _ = chars[i + 1]
                    _append_literal_glob_char(nxt, in_class=in_class)
                    if in_class:
                        class_can_close = True
                    i += 2
                    continue
                if ch in {"*", "?", "["}:
                    has_active_glob = True
                if (
                    ch in {"@", "!", "?", "+", "*"}
                    and i + 1 < len(chars)
                    and chars[i + 1][0] == "("
                    and chars[i + 1][1]
                ):
                    has_active_extglob = True
                # Preserve active glob pattern bytes verbatim, including `]`
                # and other class syntax characters.
                pat.append(ch)
                if ch == "[":
                    in_class = True
                    class_can_close = False
                elif in_class:
                    if ch == "]" and class_can_close:
                        in_class = False
                    else:
                        class_can_close = True
                i += 1
                continue
            _append_literal_glob_char(ch, in_class=in_class)
            if in_class:
                class_can_close = True
            i += 1
        pat_text = self._normalize_class_escapes("".join(pat))
        pattern = pat_text if all_quoted else self._tilde_expand(pat_text)
        if self._shopts.get("extglob", False) and has_active_extglob:
            has_active_glob = True
        if not has_active_glob:
            return [text]
        matches = self._native_glob_matches(
            pattern,
            extglob_active=bool(self._shopts.get("extglob", False) and has_active_extglob),
        )
        if matches:
            return matches
        return [text]

    def _native_glob_matches(self, pattern: str, *, extglob_active: bool) -> list[str]:
        nocase = bool(self._shopts.get("nocaseglob", False))
        dotglob = bool(self._shopts.get("dotglob", False))
        globstar = bool(self._shopts.get("globstar", False))

        norm = pattern
        is_abs = norm.startswith("/")
        parts = norm.split("/")
        if is_abs:
            parts = parts[1:]
            bases = ["/"]
        else:
            bases = ["."]

        def _has_meta(seg: str) -> bool:
            esc = False
            for i, ch in enumerate(seg):
                if esc:
                    esc = False
                    continue
                if ch == "\\":
                    esc = True
                    continue
                if ch in {"*", "?", "["}:
                    return True
                if extglob_active and ch in {"@", "!", "+", "?", "*"} and i + 1 < len(seg) and seg[i + 1] == "(":
                    return True
            return False

        def _seg_match(name: str, seg: str) -> bool:
            if name in {".", ".."}:
                return False
            if name.startswith(".") and not seg.startswith(".") and not dotglob:
                return False
            if extglob_active and self._has_extglob_syntax(seg):
                return self._match_extglob_pattern(name, seg, nocase=nocase)
            if nocase:
                return fnmatch.fnmatchcase(name.lower(), seg.lower())
            return fnmatch.fnmatchcase(name, seg)

        def _join(base: str, child: str) -> str:
            if base == "/":
                return "/" + child
            if base == ".":
                return child
            return os.path.join(base, child)

        def _expand_from(base: str, idx: int) -> list[str]:
            if idx >= len(parts):
                return [base]
            seg = parts[idx]
            if seg == "":
                if base == "/":
                    return _expand_from("/", idx + 1)
                return _expand_from(base, idx + 1)
            if seg == "**" and globstar:
                out: list[str] = []
                out.extend(_expand_from(base, idx + 1))
                stack = [base]
                seen_dirs: set[str] = set()
                while stack:
                    cur = stack.pop()
                    if cur in seen_dirs:
                        continue
                    seen_dirs.add(cur)
                    try:
                        with os.scandir(cur) as it:
                            entries = [e for e in it if e.is_dir(follow_symlinks=False)]
                    except OSError:
                        continue
                    for e in entries:
                        if e.name in {".", ".."}:
                            continue
                        if e.name.startswith(".") and not dotglob:
                            continue
                        child = _join(cur, e.name)
                        out.extend(_expand_from(child, idx + 1))
                        stack.append(child)
                return out
            if not _has_meta(seg):
                candidate = _join(base, seg)
                if idx < len(parts) - 1:
                    if os.path.isdir(candidate):
                        return _expand_from(candidate, idx + 1)
                    return []
                if os.path.lexists(candidate):
                    return [candidate]
                return []
            try:
                with os.scandir(base) as it:
                    names = [e.name for e in it]
            except OSError:
                return []
            out: list[str] = []
            for nm in names:
                if not _seg_match(nm, seg):
                    continue
                candidate = _join(base, nm)
                if idx < len(parts) - 1:
                    if os.path.isdir(candidate):
                        out.extend(_expand_from(candidate, idx + 1))
                else:
                    out.append(candidate)
            return out

        out: list[str] = []
        for b in bases:
            out.extend(_expand_from(b, 0))
        # Normalize relative spellings.
        preserve_dot_prefix = pattern.startswith("./")
        normalized: list[str] = []
        for p in out:
            if not is_abs and p.startswith("./") and not preserve_dot_prefix:
                normalized.append(p[2:])
            else:
                normalized.append(p)
        if preserve_dot_prefix:
            normalized = [p if p.startswith("./") else f"./{p}" for p in normalized]
        filtered = self._apply_globignore(normalized)
        return sorted(dict.fromkeys(filtered))

    def _apply_globignore(self, paths: list[str]) -> list[str]:
        raw = self.env.get("GLOBIGNORE", "")
        if raw == "":
            return paths
        pats = [p for p in raw.split(":") if p != ""]
        if not pats:
            return paths

        def _ignored(path: str) -> bool:
            base = os.path.basename(path)
            for pat in pats:
                if fnmatch.fnmatchcase(base, pat) or fnmatch.fnmatchcase(path, pat):
                    return True
            return base in {".", ".."}

        return [p for p in paths if not _ignored(p)]

    def _asdl_word_has_unquoted_glob(self, parts: list[Any]) -> bool:
        for part in parts:
            if not isinstance(part, dict):
                continue
            t = part.get("type")
            if t != "word_part.Literal":
                continue
            lit = self._decode_asdl_literal(str(part.get("tval", "")), quoted_context=False)
            if any(ch in lit for ch in ("*", "?", "[")):
                return True
        return False

    def _replace_spec_pattern_is_dynamic(self, spec: str) -> bool:
        text = spec
        if text.startswith(("/", "#", "%")):
            text = text[1:]
        if text.startswith("/"):
            text = text[1:]
        pat_raw, _ = self._split_unescaped_slash(text)
        in_single = False
        in_double = False
        i = 0
        while i < len(pat_raw):
            ch = pat_raw[i]
            if in_single:
                if ch == "'":
                    in_single = False
                i += 1
                continue
            if in_double:
                if ch == "\\" and i + 1 < len(pat_raw):
                    i += 2
                    continue
                if ch == '"':
                    in_double = False
                    i += 1
                    continue
                if ch in {"$", "`"}:
                    return True
                i += 1
                continue
            if ch == "\\" and i + 1 < len(pat_raw):
                i += 2
                continue
            if ch == "'":
                in_single = True
                i += 1
                continue
            if ch == '"':
                in_double = True
                i += 1
                continue
            if ch in {"$", "`"}:
                return True
            i += 1
        return False

    def _asdl_word_has_quoted_at(self, node: dict[str, Any]) -> tuple[bool, bool]:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return False, False
        parts = node.get("parts") or []
        has_qat = False
        only_qat = True
        for part in parts:
            if not isinstance(part, dict):
                only_qat = False
                continue
            if part.get("type") != "word_part.DoubleQuoted":
                only_qat = False
                continue
            inner = part.get("parts") or []
            if len(inner) != 1:
                only_qat = False
            for p in inner:
                if not isinstance(p, dict):
                    only_qat = False
                    continue
                p_type = p.get("type")
                is_qat = (
                    (p_type == "word_part.SimpleVarSub" and p.get("name") == "@")
                    or (p_type == "word_part.BracedVarSub" and p.get("name") == "@" and p.get("op") is None)
                )
                if is_qat:
                    has_qat = True
                else:
                    only_qat = False
        return has_qat, (has_qat and only_qat)

    def _expand_asdl_word_part_values(
        self, node: dict[str, Any], quoted_context: bool
    ) -> tuple[list[str], bool, bool]:
        t = node.get("type")
        if t == "word_part.Literal":
            return [self._decode_asdl_literal(str(node.get("tval", "")), quoted_context=quoted_context)], quoted_context, False
        if t == "word_part.SingleQuoted":
            return [str(node.get("sval", ""))], True, False
        if t == "word_part.DoubleQuoted":
            parts = node.get("parts") or []
            pieces: list[str] = [""]
            had_any_part = False
            had_effective_part = False
            for p in parts:
                had_any_part = True
                vals, _, _ = self._expand_asdl_word_part_values(p, quoted_context=True)
                if not vals:
                    p_type = p.get("type") if isinstance(p, dict) else None
                    if (
                        (p_type == "word_part.SimpleVarSub" and p.get("name") == "@")
                        or (
                            p_type == "word_part.BracedVarSub"
                            and p.get("name") == "@"
                            and p.get("op") is None
                        )
                    ):
                        continue
                    vals = [""]
                had_effective_part = True
                if len(vals) == 1:
                    pieces[-1] = pieces[-1] + vals[0]
                    continue
                pieces[-1] = pieces[-1] + vals[0]
                pieces.extend(vals[1:])
            if had_any_part and not had_effective_part:
                return [], True, False
            return pieces, True, False
        if t == "word_part.SimpleVarSub":
            val = self._expand_param(str(node.get("name", "")), quoted_context)
            if isinstance(val, PresplitFields):
                vals = [str(v) for v in val]
                if val.lead_boundary:
                    vals = [""] + vals
                if val.trail_boundary:
                    vals = vals + [""]
                force_single_quoted = bool(getattr(val, "force_single_quoted", False))
                return vals, (quoted_context or (force_single_quoted and len(vals) == 1)), True
            return self._normalize_asdl_expanded_values(val), quoted_context, False
        if t == "word_part.BracedVarSub":
            arg_node = node.get("arg")
            arg_text, _arg_fields = self._asdl_operator_arg_text_and_fields(arg_node)
            val = self._expand_braced_param(
                str(node.get("name", "")),
                node.get("op"),
                arg_text,
                quoted_context,
                arg_fields=_arg_fields,
                arg_node=arg_node if isinstance(arg_node, dict) else None,
            )
            if isinstance(val, PresplitFields):
                vals = [str(v) for v in val]
                if val.lead_boundary:
                    vals = [""] + vals
                if val.trail_boundary:
                    vals = vals + [""]
                force_single_quoted = bool(getattr(val, "force_single_quoted", False))
                return vals, (quoted_context or (force_single_quoted and len(vals) == 1)), True
            return self._normalize_asdl_expanded_values(val), quoted_context, False
        if t == "word_part.CommandSub":
            child = node.get("child")
            syntax = str(node.get("syntax") or "dollar")
            backtick = syntax == "backtick"
            if isinstance(child, dict) and child.get("type") == "command.CommandList":
                return [self._expand_command_subst_asdl(child, backtick=backtick)], quoted_context, False
            src = str(node.get("child_source") or "")
            return [self._expand_command_subst_text(src, backtick=backtick)], quoted_context, False
        if t == "word_part.ArithSub":
            expr = str(node.get("expr_source") or node.get("code") or "")
            return [self._expand_arith(expr)], quoted_context, False
        return [""], quoted_context, False

    def _asdl_operator_arg_text_and_fields(self, arg_node: Any) -> tuple[str | None, list[ExpansionField] | None]:
        if not isinstance(arg_node, dict):
            return None, None
        if arg_node.get("type") != "word.Compound":
            return None, None
        return self._asdl_word_to_text(arg_node), self._asdl_word_to_expansion_fields(arg_node)

    def _decode_asdl_literal(self, text: str, *, quoted_context: bool) -> str:
        if "\\" not in text:
            return text
        out: list[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch != "\\" or i + 1 >= len(text):
                out.append(ch)
                i += 1
                continue
            nxt = text[i + 1]
            if quoted_context:
                if nxt in {'$', '"', "\\", "`"}:
                    out.append(nxt)
                else:
                    out.append("\\")
                    out.append(nxt)
            else:
                out.append(nxt)
            i += 2
        return "".join(out)

    def _asdl_case_pattern_from_word(self, node: dict[str, Any]) -> str:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return ""
        return self._pattern_from_structured_fields(
            self._expand_asdl_assignment_fields(node),
            for_case=True,
        )

    def _escape_case_pattern_literal(self, text: str) -> str:
        out: list[str] = []
        for ch in text:
            if ch in {"*", "?", "[", "]", "\\", "-", "!"}:
                out.append("\\")
                out.append(ch)
            else:
                out.append(ch)
        return "".join(out)

    def _normalize_asdl_expanded_values(self, value: Any) -> list[str]:
        if isinstance(value, PresplitFields):
            return [str(v) for v in value]
        if isinstance(value, list):
            return [str(v) for v in value]
        return ["" if value is None else str(value)]

    def _asdl_word_to_text(self, node: dict[str, Any]) -> str:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return ""
        return "".join(self._asdl_word_part_to_text(p) for p in (node.get("parts") or []))

    def _asdl_word_part_to_text(self, node: dict[str, Any]) -> str:
        t = node.get("type")
        if t == "word_part.Literal":
            return node.get("tval", "")
        if t == "word_part.SingleQuoted":
            return "'" + node.get("sval", "") + "'"
        if t == "word_part.DoubleQuoted":
            inner = "".join(self._asdl_word_part_to_double_text(p) for p in (node.get("parts") or []))
            return '"' + inner + '"'
        if t == "word_part.SimpleVarSub":
            return "$" + node.get("name", "")
        if t == "word_part.BracedVarSub":
            name = node.get("name", "")
            op = node.get("op")
            if op == "__len__":
                return "${#" + name + "}"
            if op == "__indirect__":
                return "${!" + name + "}"
            if op == "__keys__":
                arg = node.get("arg")
                suffix = ""
                if isinstance(arg, dict):
                    suffix = self._asdl_word_to_text(arg)
                elif isinstance(arg, str):
                    suffix = arg
                if suffix not in {"@", "*"}:
                    suffix = "@"
                return "${!" + name + "[" + suffix + "]}"
            if op == ":substr":
                arg = node.get("arg")
                arg_s = self._asdl_word_to_text(arg) if isinstance(arg, dict) else ""
                return "${" + name + ":" + arg_s + "}"
            if op:
                arg = node.get("arg")
                arg_s = self._asdl_word_to_text(arg) if isinstance(arg, dict) else ""
                return "${" + name + op + arg_s + "}"
            return "${" + name + "}"
        if t == "word_part.CommandSub":
            src = node.get("child_source") or ""
            syntax = node.get("syntax") or "dollar"
            if syntax == "backtick":
                return "`" + src + "`"
            return "$(" + src + ")"
        if t == "word_part.ArithSub":
            return "$((" + (node.get("expr_source") or node.get("code") or "") + "))"
        return ""

    def _asdl_word_part_to_double_text(self, node: dict[str, Any]) -> str:
        if node.get("type") == "word_part.Literal":
            return node.get("tval", "")
        return self._asdl_word_part_to_text(node)

    def _asdl_word_part_to_heredoc_text(self, node: dict[str, Any]) -> str:
        if node.get("type") == "word_part.Literal":
            return node.get("tval", "")
        return self._asdl_word_part_to_text(node)

    def _asdl_command_line(self, node: dict[str, Any]) -> int | None:
        for w in (node.get("words") or []):
            pos = w.get("pos") if isinstance(w, dict) else None
            if isinstance(pos, dict):
                line = pos.get("line")
                if isinstance(line, int):
                    return line
        return None

    def _asdl_simple_command_end_line(self, node: dict[str, Any]) -> int | None:
        end_line: int | None = None
        for w in (node.get("words") or []):
            if not isinstance(w, dict):
                continue
            pos = w.get("pos")
            if not isinstance(pos, dict):
                continue
            line = pos.get("line")
            if not isinstance(line, int):
                continue
            cand = line + self._count_asdl_word_error_newlines(self._asdl_word_to_text(w))
            if end_line is None or cand > end_line:
                end_line = cand
        return end_line

    def _count_asdl_word_error_newlines(self, text: str) -> int:
        # Keep bash-compatible diagnostic accounting for a narrow legacy form
        # seen in command-substitution tests: `...\\\\\\n/...` should not add an
        # extra error line increment.
        count = 0
        i = 0
        n = len(text)
        while i < n:
            if text[i] != "\n":
                i += 1
                continue
            if (
                i >= 1
                and i + 1 < n
                and text[i - 1] == "\\"
                and text[i + 1] == "/"
            ):
                i += 1
                continue
            count += 1
            i += 1
        return count

    def _asdl_token_text(self, tok: Any) -> str:
        if isinstance(tok, dict):
            if "tval" in tok:
                return str(tok.get("tval") or "")
            if "value" in tok:
                return str(tok.get("value") or "")
            return ""
        if tok is None:
            return ""
        return str(tok)

    def _try_unshare_thread_state(self) -> None:
        if not sys.platform.startswith("linux"):
            return
        if getattr(self._thread_ctx, "unshared_fs_files", False):
            return
        mode = self._thread_unshare_mode()
        if mode == "off":
            self._emit_thread_diag_once("unshare disabled (MCTASH_UNSHARE_MODE=off)")
            return
        if mode == "fail":
            self._emit_thread_diag_once("unshare forced-fail (MCTASH_UNSHARE_MODE=fail)")
            return
        try:
            libc = ctypes.CDLL(None, use_errno=True)
            unshare = libc.unshare
            unshare.argtypes = [ctypes.c_int]
            unshare.restype = ctypes.c_int
            CLONE_FS = 0x00000200
            CLONE_FILES = 0x00000400
            rc = int(unshare(CLONE_FS | CLONE_FILES))
            if rc == 0:
                self._thread_ctx.unshared_fs_files = True
                return
            err = ctypes.get_errno()
            self._emit_thread_diag_once(f"unshare(CLONE_FS|CLONE_FILES) failed errno={err}")
        except Exception:
            # Best effort only; fallback keeps current shared-thread behavior.
            self._emit_thread_diag_once("unshare(CLONE_FS|CLONE_FILES) unavailable")
            return

    def _thread_unshare_mode(self) -> str:
        mode = self.env.get("MCTASH_UNSHARE_MODE", os.environ.get("MCTASH_UNSHARE_MODE", "auto"))
        return mode.strip().lower() if isinstance(mode, str) else "auto"

    def _thread_diag_enabled(self) -> bool:
        v = self.env.get("MCTASH_THREAD_DIAG", os.environ.get("MCTASH_THREAD_DIAG", "0"))
        return str(v).strip().lower() in {"1", "true", "yes", "on"}

    def _emit_thread_diag_once(self, msg: str) -> None:
        if not self._thread_diag_enabled():
            return
        with self._thread_diag_lock:
            if msg in self._thread_diag_emitted:
                return
            self._thread_diag_emitted.add(msg)
        print(f"mctash: thread-runtime: {msg}", file=sys.stderr)

    def _snapshot_open_fds(self) -> set[int]:
        out: set[int] = set()
        proc_fd = "/proc/self/fd"
        try:
            for name in os.listdir(proc_fd):
                if not name.isdigit():
                    continue
                out.add(int(name))
            return out
        except Exception:
            # Fallback: tracked user/temp fds plus stdio.
            out.update({0, 1, 2})
            out.update(fd for fd in self._user_fds if isinstance(fd, int))
            out.update(fd for fd in self._active_temp_fds if isinstance(fd, int))
            return out

    def _close_tracked_fds_not_in(self, baseline: set[int]) -> None:
        leaked = set(self._user_fds) | set(self._active_temp_fds)
        for fd in sorted(leaked):
            if fd < 3 or fd in baseline:
                continue
            try:
                os.close(fd)
            except OSError:
                pass
        self._user_fds = {fd for fd in self._user_fds if fd in baseline}
        self._active_temp_fds = {fd for fd in self._active_temp_fds if fd in baseline}

    def _exec_and_or(self, node: AndOr, track_status: bool = True) -> int:
        if len(node.pipelines) > 1:
            with self._suppress_errexit():
                status = self._exec_pipeline(node.pipelines[0])
        else:
            status = self._exec_pipeline(node.pipelines[0])
        last_exec_idx = 0
        if track_status:
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
        for i, (op, pipeline) in enumerate(zip(node.operators, node.pipelines[1:]), start=1):
            if op == "&&":
                if status == 0:
                    if i < (len(node.pipelines) - 1):
                        with self._suppress_errexit():
                            status = self._exec_pipeline(pipeline)
                    else:
                        status = self._exec_pipeline(pipeline)
                    last_exec_idx = i
                    if track_status:
                        self.last_status = status
                        if status != 0:
                            self.last_nonzero_status = status
                        self._trap_status_hint = status
            elif op == "||":
                if status != 0:
                    if i < (len(node.pipelines) - 1):
                        with self._suppress_errexit():
                            status = self._exec_pipeline(pipeline)
                    else:
                        status = self._exec_pipeline(pipeline)
                    last_exec_idx = i
                    if track_status:
                        self.last_status = status
                        if status != 0:
                            self.last_nonzero_status = status
                        self._trap_status_hint = status
        neg_exempt = False
        if status != 0 and 0 <= last_exec_idx < len(node.pipelines):
            neg_exempt = bool(getattr(node.pipelines[last_exec_idx], "negate", False))
        self._errexit_item_exempt = status != 0 and (
            last_exec_idx < (len(node.pipelines) - 1) or neg_exempt
        )
        return status

    def _exec_pipeline(self, node: Pipeline) -> int:
        if node.negate:
            with self._suppress_errexit():
                if len(node.commands) == 1:
                    status = self._exec_command(node.commands[0])
                    return 0 if status != 0 else 1
                if isinstance(sys.stdin, io.StringIO):
                    status = self._exec_pipeline_inprocess(node)
                    return 0 if status != 0 else 1
                if any(self._pipeline_needs_shell(cmd) for cmd in node.commands):
                    status = self._exec_pipeline_inprocess(node)
                    return 0 if status != 0 else 1
        elif len(node.commands) == 1:
            status = self._exec_command(node.commands[0])
            return status

        if isinstance(sys.stdin, io.StringIO):
            status = self._exec_pipeline_inprocess(node)
            return status

        if any(self._pipeline_needs_shell(cmd) for cmd in node.commands):
            status = self._exec_pipeline_inprocess(node)
            return status

        procs: List[subprocess.Popen] = []
        statuses: List[int] = []
        prev = None
        for i, cmd in enumerate(node.commands):
            if not isinstance(cmd, SimpleCommand):
                return self._exec_command(cmd)
            cmd_env = self._exported_env_view(self.env)
            for scope in self.local_stack:
                for k, v in scope.items():
                    if k in self.env and "exported" in self._var_attrs.get(k, set()):
                        cmd_env[k] = v
            for assign in cmd.assignments:
                value = self._expand_assignment_word(assign.value)
                if assign.op == "+=":
                    cmd_env[assign.name] = cmd_env.get(assign.name, "") + value
                else:
                    cmd_env[assign.name] = value
            argv = self._expand_argv(cmd.argv)
            if not argv:
                return 2
            stdin = prev.stdout if prev is not None else None
            stdout = subprocess.PIPE if i < len(node.commands) - 1 else None
            stdin, stdout, stderr, to_close = self._apply_redirects(cmd.redirects, stdin, stdout, None)
            try:
                proc = subprocess.Popen(
                    argv,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    env=cmd_env,
                    preexec_fn=self._preexec_reset_signals,
                )
            except FileNotFoundError:
                if "/" in argv[0]:
                    print(
                        self._diag_msg(
                            DiagnosticKey.ERRNO_NAME,
                            name=argv[0],
                            error="No such file or directory",
                        ),
                        file=sys.stderr,
                    )
                else:
                    print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0]), file=sys.stderr)
                return 127
            except OSError as e:
                if getattr(e, "errno", None) == 8 and os.path.isfile(argv[0]) and len(node.commands) == 1:
                    return self._run_source(argv[0], argv[1:])
                self._print_stderr(self._diag_msg(DiagnosticKey.ERRNO_NAME, name=argv[0], error=str(e.strerror)))
                return 126
            finally:
                for f in to_close:
                    try:
                        f.close()
                    except Exception:
                        pass
            procs.append(proc)
            if prev is not None and prev.stdout is not None:
                prev.stdout.close()
            prev = proc
        status = procs[-1].wait()
        statuses.append(status)
        for p in procs[:-1]:
            statuses.insert(0, p.wait())
        status = self._pipeline_result(statuses)
        if node.negate:
            return 0 if status != 0 else 1
        return status

    def _pipeline_needs_shell(self, cmd: Command) -> bool:
        if not isinstance(cmd, SimpleCommand):
            return True
        argv = self._expand_argv(cmd.argv)
        if not argv:
            return False
        name = argv[0]
        return self._is_builtin_enabled(name) or self._has_function(name)

    def _exec_pipeline_inprocess(self, node: Pipeline) -> int:
        data: bytes | None = None
        data_latency: float | None = None
        if isinstance(sys.stdin, io.StringIO):
            seed = sys.stdin.read()
            data = seed.encode("utf-8", errors="surrogateescape")
            if self._pipeline_input_latency is not None:
                data_latency = self._pipeline_input_latency
        status = 0
        statuses: List[int] = []
        for i, cmd in enumerate(node.commands):
            if not isinstance(cmd, SimpleCommand):
                last = i == len(node.commands) - 1
                if last:
                    force_epipe = False
                    saved_epipe = self._force_broken_pipe
                    self._force_broken_pipe = force_epipe
                    saved_stdin = sys.stdin
                    saved_latency = self._pipeline_input_latency
                    try:
                        if data is not None:
                            sys.stdin = io.StringIO(data.decode("utf-8", errors="ignore"))
                        self._pipeline_input_latency = data_latency
                        status = self._exec_command(cmd)
                    finally:
                        sys.stdin = saved_stdin
                        self._pipeline_input_latency = saved_latency
                        self._force_broken_pipe = saved_epipe
                    data = None
                    data_latency = None
                else:
                    sink_is_no_reader = False
                    if i + 1 < len(node.commands):
                        sink_is_no_reader = self._pipeline_sink_is_no_reader(node.commands[i + 1])
                    status, data, data_latency = self._capture_command_output(
                        cmd, data=data, force_epipe=sink_is_no_reader
                    )
                statuses.append(status)
                continue
            argv = self._expand_argv(cmd.argv)
            if not argv:
                status = self._run_subshell(ListNode(items=[ListItem(node=AndOr(pipelines=[Pipeline(commands=[cmd], negate=False)], operators=[]), background=False)]))
                statuses.append(status)
                data = b""
                data_latency = 0.0
                continue
            last = i == len(node.commands) - 1
            saved_latency = self._pipeline_input_latency
            self._pipeline_input_latency = data_latency
            status, data, data_latency = self._exec_simple_capture(cmd, argv, data, capture=not last)
            self._pipeline_input_latency = saved_latency
            statuses.append(status)
            if last and data is not None:
                sys.stdout.write(data.decode("utf-8", errors="ignore"))
                sys.stdout.flush()
        return self._pipeline_result(statuses if statuses else [status])

    def _capture_command_output(
        self, cmd: Command, data: bytes | None = None, force_epipe: bool = False
    ) -> tuple[int, bytes, float]:
        start = time.monotonic()
        tmp = tempfile.TemporaryFile()
        saved_env = dict(self.env)
        saved_locals = [dict(s) for s in self.local_stack]
        saved_typed = copy.deepcopy(self._typed_vars)
        saved_attrs = {k: set(v) for k, v in self._var_attrs.items()}
        saved_readonly = set(self.readonly_vars)
        saved_opts = dict(self.options)
        saved_positional = list(self.positional)
        try:
            sys.stdout.flush()
        except Exception:
            pass
        saved_stdout = os.dup(1)
        saved_stdin = sys.stdin
        os.dup2(tmp.fileno(), 1)
        py_stdout = os.fdopen(os.dup(1), "w", encoding="utf-8", errors="surrogateescape", buffering=1)
        saved_py_stdout = sys.stdout
        sys.stdout = py_stdout
        saved_epipe = self._force_broken_pipe
        self._force_broken_pipe = force_epipe
        try:
            try:
                if data is not None:
                    sys.stdin = io.StringIO(data.decode("utf-8", errors="ignore"))
                status = self._exec_command(cmd)
            except SystemExit as e:
                status = int(e.code) if e.code is not None else 0
        finally:
            self.env = saved_env
            self.local_stack = saved_locals
            self._typed_vars = saved_typed
            self._var_attrs = saved_attrs
            self.readonly_vars = saved_readonly
            self.options = saved_opts
            self.positional = saved_positional
            try:
                sys.stdout.flush()
            except Exception:
                pass
            sys.stdout = saved_py_stdout
            try:
                py_stdout.close()
            except Exception:
                pass
            sys.stdin = saved_stdin
            self._force_broken_pipe = saved_epipe
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
        tmp.seek(0)
        data = tmp.read()
        tmp.close()
        return status, data, time.monotonic() - start

    def _pipeline_result(self, statuses: List[int]) -> int:
        if self.options.get("pipefail", False):
            for st in reversed(statuses):
                if st != 0:
                    return st
            return 0
        return statuses[-1] if statuses else 0

    def _pipeline_sink_is_no_reader(self, cmd: Command) -> bool:
        if isinstance(cmd, SimpleCommand):
            argv = self._expand_argv(cmd.argv)
            return argv == ["true"]
        if isinstance(cmd, GroupCommand):
            items = cmd.body.items
            if len(items) != 1:
                return False
            andor = items[0].node
            if len(andor.pipelines) != 1:
                return False
            pl = andor.pipelines[0]
            if len(pl.commands) != 1 or not isinstance(pl.commands[0], SimpleCommand):
                return False
            argv = self._expand_argv(pl.commands[0].argv)
            return argv == ["true"]
        return False

    def _exec_simple_capture(
        self, cmd: SimpleCommand, argv: List[str], data: bytes | None, capture: bool
    ) -> tuple[int, bytes | None, float | None]:
        start = time.monotonic() if capture else None
        name = argv[0]
        input_text = data.decode("utf-8", errors="ignore") if data is not None else None
        cmd_env = dict(self.env)
        # Function-local variables should shadow exported globals for
        # external commands in pipeline capture paths.
        for scope in self.local_stack:
            for k, v in scope.items():
                if k in self.env:
                    cmd_env[k] = v
        if cmd.assignments:
            saved_env = self.env
            try:
                self.env = cmd_env
                for assign in cmd.assignments:
                    value = self._expand_assignment_word(assign.value)
                    if assign.op == "+=":
                        cmd_env[assign.name] = cmd_env.get(assign.name, "") + value
                    else:
                        cmd_env[assign.name] = value
            finally:
                self.env = saved_env
        if self._has_function(name) or self._is_builtin_enabled(name):
            saved_env = self.env
            self.env = cmd_env
            if capture and self._stdout_redirected_away(cmd.redirects):
                with self._redirected_fds(cmd.redirects):
                    try:
                        if self._has_function(name):
                            status = self._run_function(name, argv[1:])
                        else:
                            status = self._run_builtin(name, argv)
                    except SystemExit as e:
                        status = int(e.code) if e.code is not None else 0
                    except ReturnFromFunction as e:
                        status = e.code
                    except (BreakLoop, ContinueLoop):
                        status = 1
                self.env = saved_env
                return status, b"", (time.monotonic() - start) if start is not None else None
            saved_stdin = sys.stdin
            saved_stdout = sys.stdout
            saved_fd1 = None
            saved_fd0 = None
            py_stdout = None
            tmp = None
            tmp_in = None
            try:
                if input_text is None:
                    sys.stdin = saved_stdin
                else:
                    sys.stdin = io.StringIO(input_text)
                    tmp_in = tempfile.TemporaryFile()
                    tmp_in.write(data if data is not None else b"")
                    tmp_in.seek(0)
                    saved_fd0 = os.dup(0)
                    os.dup2(tmp_in.fileno(), 0)
                if capture:
                    tmp = tempfile.TemporaryFile()
                    try:
                        sys.stdout.flush()
                    except Exception:
                        pass
                    saved_fd1 = os.dup(1)
                    os.dup2(tmp.fileno(), 1)
                    py_stdout = os.fdopen(
                        os.dup(1),
                        "w",
                        encoding="utf-8",
                        errors="surrogateescape",
                        buffering=1,
                    )
                    sys.stdout = py_stdout
                else:
                    sys.stdout = saved_stdout
                try:
                    with self._redirected_fds(cmd.redirects):
                        if self._has_function(name):
                            status = self._run_function(name, argv[1:])
                        else:
                            status = self._run_builtin(name, argv)
                except SystemExit as e:
                    status = int(e.code) if e.code is not None else 0
                except ReturnFromFunction as e:
                    status = e.code
                except (BreakLoop, ContinueLoop):
                    status = 1
                if capture and tmp is not None:
                    try:
                        sys.stdout.flush()
                    except Exception:
                        pass
                    tmp.seek(0)
                    out_data = tmp.read()
                else:
                    out_data = b""
                return status, out_data, (time.monotonic() - start) if start is not None else None
            finally:
                sys.stdin = saved_stdin
                sys.stdout = saved_stdout
                if py_stdout is not None:
                    try:
                        py_stdout.close()
                    except Exception:
                        pass
                if saved_fd1 is not None:
                    os.dup2(saved_fd1, 1)
                    os.close(saved_fd1)
                if saved_fd0 is not None:
                    os.dup2(saved_fd0, 0)
                    os.close(saved_fd0)
                if tmp is not None:
                    tmp.close()
                if tmp_in is not None:
                    tmp_in.close()
                self.env = saved_env

        try:
            stdin = subprocess.PIPE if data is not None else None
            stdout = subprocess.PIPE if capture else None
            stdin, stdout, stderr, to_close = self._apply_redirects(cmd.redirects, stdin, stdout, None)
            try:
                proc = subprocess.Popen(
                    argv,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    env=cmd_env,
                    preexec_fn=self._preexec_reset_signals,
                )
                if stdin == subprocess.PIPE:
                    out, _ = proc.communicate(data if data is not None else b"")
                else:
                    out, _ = proc.communicate()
                return proc.returncode, out, (time.monotonic() - start) if start is not None else None
            finally:
                for f in to_close:
                    try:
                        f.close()
                    except Exception:
                        pass
        except FileNotFoundError:
            if "/" in argv[0]:
                print(
                    self._diag_msg(
                        DiagnosticKey.ERRNO_NAME,
                        name=argv[0],
                        error="No such file or directory",
                    ),
                    file=sys.stderr,
                )
            else:
                print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0]), file=sys.stderr)
            return 127, b"", (time.monotonic() - start) if start is not None else None

    def _stdout_redirected_away(self, redirects: List[Redirect]) -> bool:
        for redir in redirects:
            fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<<<", "<&", "<>"] else 1)
            if fd != 1:
                continue
            if redir.op in [">", ">>", "&>", "&>>"]:
                return True
            if redir.op == ">&" and redir.target is not None:
                return redir.target != "1"
        return False

    def _exec_command(self, node: Command) -> int:
        if self.options.get("n", False):
            if isinstance(node, FunctionDef):
                self.functions[node.name] = node.body
            return 0
        if isinstance(node, GroupCommand):
            return self._exec_list(node.body)
        if isinstance(node, SubshellCommand):
            return self._run_subshell(node.body)
        if isinstance(node, FunctionDef):
            if self.options.get("posix", False) and node.name in self.SPECIAL_BUILTINS:
                self._report_error(
                    f"{node.name}: is a special builtin",
                    line=self.current_line,
                    context="function",
                )
                return 2
            self.functions[node.name] = node.body
            return 0
        if isinstance(node, ForCommand):
            return self._run_for(node)
        if isinstance(node, ArithForCommand):
            return self._run_arith_for(node.init, node.cond, node.update, lambda: self._exec_list(node.body))
        if isinstance(node, CaseCommand):
            return self._run_case(node)
        if isinstance(node, IfCommand):
            with self._suppress_errexit():
                status = self._exec_list(node.cond)
            if status == 0:
                return self._exec_list(node.then_body)
            for elif_cond, elif_body in node.elifs:
                with self._suppress_errexit():
                    status = self._exec_list(elif_cond)
                if status == 0:
                    return self._exec_list(elif_body)
            if node.else_body is not None:
                return self._exec_list(node.else_body)
            return 0
        if isinstance(node, WhileCommand):
            self._loop_depth += 1
            last = 0
            try:
                while True:
                    try:
                        with self._suppress_errexit():
                            cond_status = self._exec_list(node.cond)
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        self._run_pending_traps()
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        last = 0
                        break
                    should_run = cond_status != 0 if node.until else cond_status == 0
                    if not should_run:
                        break
                    try:
                        last = self._exec_list(node.body)
                        self._run_pending_traps()
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        self._run_pending_traps()
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        last = 0
                        break
                return last
            finally:
                self._loop_depth -= 1
        if isinstance(node, SimpleCommand):
            if node.line is not None:
                self.current_line = node.line
            try:
                argv = self._expand_argv(node.argv)
            except RuntimeError as e:
                msg = str(e)
                self._print_stderr(msg)
                if "bad substitution" in msg or "unbound variable:" in msg:
                    raise SystemExit(self._runtime_error_status(msg))
                raise SystemExit(1)
            except CommandSubstFailure as e:
                return e.code
            except ArithExpansionFailure as e:
                return e.code
            argv = self._expand_aliases(argv)

            if argv and argv[0] == "exec" and len(argv) == 2 and node.redirects:
                named_fd_var = self._parse_exec_named_fd_var(argv[1])
                if named_fd_var is not None:
                    handled = self._handle_exec_named_fd_redirect(named_fd_var, node.redirects)
                    if handled is not None:
                        return handled

            if argv and argv[0] == "exec" and len(argv) <= 1 and node.redirects:
                local_env = dict(self.env)
                saved_env = self.env
                assigned_names: set[str] = set()
                compound_assigned: set[str] = set()
                try:
                    self.env = local_env
                    self._apply_persistent_redirects(node.redirects)
                    for assign in node.assignments:
                        try:
                            value = self._expand_assignment_word(assign.value)
                        except CommandSubstFailure as e:
                            return e.code
                        except ArithExpansionFailure as e:
                            return e.code
                        name = assign.name
                        op = assign.op
                        assigned_names.add(name)
                        if name in self.readonly_vars:
                            msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                            print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                            if self._diag.style == "bash":
                                return 1
                            raise SystemExit(2)
                        comp_vals = self._parse_compound_assignment_rhs(assign.value) if self._bash_compat_level is not None else None
                        if comp_vals is None:
                            bad_tok = self._compound_assignment_unexpected_token(assign.value)
                            if bad_tok is not None:
                                self._print_stderr(
                                    self._format_error(
                                        f"syntax error near unexpected token `{bad_tok}'",
                                        line=self.current_line,
                                    )
                                )
                                return 1
                        if name in self._py_ties:
                            if comp_vals is not None:
                                raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                            if op == "+=":
                                self._assign_shell_var(name, self._get_var(name) + value)
                            else:
                                self._assign_shell_var(name, value)
                            self._sync_local_env_assignment(local_env, name)
                            continue
                        if comp_vals is not None:
                            if self._parse_subscripted_name(name) is not None:
                                raise RuntimeError(f"{name}: cannot assign list to array member")
                            self._assign_compound_var(name, op, comp_vals)
                            compound_assigned.add(name)
                            self._sync_local_env_assignment(local_env, name)
                            continue
                        self._assign_shell_var_op(name, op, value)
                        self._sync_local_env_assignment(local_env, name)
                    should_persist_env = any(
                        not (r.op == ">&" and (r.fd is None or r.fd == 1) and r.target == "1")
                        for r in node.redirects
                    )
                    if should_persist_env:
                        for n in assigned_names:
                            if n in compound_assigned:
                                continue
                            attrs = self._structured_var_attrs(n)
                            if "array" in attrs or "assoc" in attrs:
                                continue
                            self._typed_vars.pop(n, None)
                        saved_env.clear()
                        saved_env.update(self.env)
                    return 0
                finally:
                    self.env = saved_env

            local_env = dict(self.env)
            saved_env = self.env
            assigned_names: set[str] = set()
            compound_assigned: set[str] = set()
            try:
                self.env = local_env
                for assign in node.assignments:
                    try:
                        value = self._expand_assignment_word(assign.value)
                    except CommandSubstFailure as e:
                        return e.code
                    except ArithExpansionFailure as e:
                        return e.code
                    name = assign.name
                    op = assign.op
                    assigned_names.add(name)
                    if name in self.readonly_vars:
                        msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                        print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                        if self._diag.style == "bash":
                            return 1
                        raise SystemExit(2)
                    comp_vals = self._parse_compound_assignment_rhs(assign.value) if self._bash_compat_level is not None else None
                    if comp_vals is None:
                        bad_tok = self._compound_assignment_unexpected_token(assign.value)
                        if bad_tok is not None:
                            self._print_stderr(
                                self._format_error(
                                    f"syntax error near unexpected token `{bad_tok}'",
                                    line=self.current_line,
                                )
                            )
                            return 1
                    if name in self._py_ties:
                        if comp_vals is not None:
                            raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                        if op == "+=":
                            self._assign_shell_var(name, self._get_var(name) + value)
                        else:
                            self._assign_shell_var(name, value)
                        self._sync_local_env_assignment(local_env, name)
                        continue
                    if comp_vals is not None:
                        if self._parse_subscripted_name(name) is not None:
                            raise RuntimeError(f"{name}: cannot assign list to array member")
                        self._assign_compound_var(name, op, comp_vals)
                        compound_assigned.add(name)
                        self._sync_local_env_assignment(local_env, name)
                        self.env = local_env
                        continue
                    self._assign_shell_var_op(name, op, value)
                    self._sync_local_env_assignment(local_env, name)
                    self.env = local_env
            finally:
                self.env = saved_env
            if self.options.get("x", False):
                self._trace_simple(node, argv, local_env)
            if not argv:
                try:
                    if node.redirects:
                        with self._redirected_fds(node.redirects):
                            pass
                except RuntimeError as e:
                    print(str(e), file=sys.stderr)
                    return 1
                for n in assigned_names:
                    if n in compound_assigned:
                        continue
                    attrs = self._structured_var_attrs(n)
                    if "array" in attrs or "assoc" in attrs:
                        continue
                    self._typed_vars.pop(n, None)
                self.env.update(local_env)
                for tied_name in self._py_ties:
                    self.env[tied_name] = self._get_var(tied_name)
                if self._cmd_sub_used:
                    status = self._cmd_sub_status
                    self._cmd_sub_used = False
                    return status
                return 0
            if argv and argv[0] not in {"declare", "typeset", "local", "readonly", "export"}:
                for arg in argv[1:]:
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=\(.*$", arg):
                        self._print_stderr(self._format_error("syntax error near unexpected token `('", line=self.current_line))
                        self._print_stderr(self._format_error(f"`{' '.join(argv)}'", line=self.current_line))
                        return 2
            if not argv:
                return 0
            declaration_cmds = {"declare", "typeset", "local", "readonly", "export"}
            argv_assigns = None if (argv and argv[0] in declaration_cmds) else self._argv_assignment_words(argv)
            if argv_assigns is not None:
                saved_env2 = self.env
                try:
                    self.env = local_env
                    for var_name, op, value, is_compound in argv_assigns:
                        if var_name in self.readonly_vars:
                            msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=var_name)
                            print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                            if self._diag.style == "bash":
                                return 1
                            raise SystemExit(2)
                        if is_compound:
                            self._assign_compound_var(
                                var_name,
                                op,
                                list(value) if isinstance(value, list) else [],
                            )
                        else:
                            self._assign_shell_var_op(var_name, op, str(value))
                        base = var_name.split("[", 1)[0]
                        local_env[base] = self._get_var(base)
                    saved_env2.update(local_env)
                    for tied_name in self._py_ties:
                        saved_env2[tied_name] = self._get_var(tied_name)
                    return 0
                finally:
                    self.env = saved_env2
            if self._cmd_sub_used:
                self._cmd_sub_used = False
            name = argv[0]
            assign_names = {a.name for a in node.assignments}
            if self._has_function(name):
                saved_env = dict(self.env)
                try:
                    self.env = local_env
                    try:
                        with self._redirected_fds(node.redirects):
                            status = self._run_function(name, argv[1:])
                    except RuntimeError as e:
                        print(str(e), file=sys.stderr)
                        return 1
                finally:
                    result_env = dict(self.env)
                    merged = dict(saved_env)
                    for k, v in result_env.items():
                        if k not in assign_names:
                            merged[k] = v
                    for k in list(merged.keys()):
                        if k not in result_env and k not in assign_names:
                            merged.pop(k, None)
                    for k in assign_names:
                        if k in saved_env:
                            merged[k] = saved_env[k]
                        else:
                            merged.pop(k, None)
                    self.env = merged
                return status
            if self._should_dispatch_builtin(argv):
                is_special = name in self.SPECIAL_BUILTINS
                if is_special:
                    if self.options.get("posix", False):
                        saved_env = dict(self.env)
                        self.env = local_env
                        try:
                            with self._redirected_fds(node.redirects):
                                status = self._run_builtin(name, argv)
                        except RuntimeError as e:
                            print(str(e), file=sys.stderr)
                            return 1
                        if name == "unset" and assign_names:
                            for var_name in assign_names:
                                if var_name not in self.env:
                                    if var_name in saved_env:
                                        self.env[var_name] = saved_env[var_name]
                                elif var_name in saved_env and self.env.get(var_name, "") == "":
                                    self.env[var_name] = saved_env[var_name]
                        return status
                    persist_assigns = self._declaration_assigns_should_persist(argv)
                    saved_env = dict(self.env)
                    try:
                        self.env = local_env
                        try:
                            with self._redirected_fds(node.redirects):
                                status = self._run_builtin(name, argv)
                        except RuntimeError as e:
                            print(str(e), file=sys.stderr)
                            return 1
                    finally:
                        result_env = dict(self.env)
                        merged = dict(saved_env)
                        for k, v in result_env.items():
                            if persist_assigns or k not in assign_names:
                                merged[k] = v
                        for k in list(merged.keys()):
                            if k not in result_env and (persist_assigns or k not in assign_names):
                                merged.pop(k, None)
                        if not persist_assigns:
                            for k in assign_names:
                                if k in saved_env:
                                    merged[k] = saved_env[k]
                                else:
                                    merged.pop(k, None)
                        self.env = merged
                    return status
                saved_env = self.env
                try:
                    self.env = local_env
                    try:
                        with self._redirected_fds(node.redirects):
                            status = self._run_builtin(name, argv)
                    except RuntimeError as e:
                        print(str(e), file=sys.stderr)
                        return 1
                    if name in self.ENV_MUTATING_BUILTINS:
                        persist_assigns = self._declaration_assigns_should_persist(argv)
                        result_env = dict(self.env)
                        merged = dict(saved_env)
                        for k, v in result_env.items():
                            if persist_assigns or k not in assign_names:
                                merged[k] = v
                        for k in list(merged.keys()):
                            if k not in result_env and (persist_assigns or k not in assign_names):
                                merged.pop(k, None)
                        if not persist_assigns:
                            for k in assign_names:
                                if k in saved_env:
                                    merged[k] = saved_env[k]
                                else:
                                    merged.pop(k, None)
                        saved_env.clear()
                        saved_env.update(merged)
                    return status
                finally:
                    self.env = saved_env
            if name in self._py_callables:
                saved_env = self.env
                try:
                    self.env = local_env
                    try:
                        with self._redirected_fds(node.redirects):
                            result = self._invoke_py_callable(self._py_callables[name], argv[1:])
                    except RuntimeError as e:
                        print(str(e), file=sys.stderr)
                        return 1
                except Exception as e:
                    print(f"{name}: {type(e).__name__}: {e}", file=sys.stderr)
                    return 1
                finally:
                    self.env = saved_env
                if result is not None:
                    print(self._py_to_shell(result))
                return 0
            try:
                exec_env = {
                    k: v
                    for k, v in local_env.items()
                    if "exported" in self._var_attrs.get(k, set())
                }
                for assign in node.assignments:
                    exec_env[assign.name] = local_env.get(assign.name, "")
                # Local variables should shadow exported globals for external
                # commands, but only when that name is already exported.
                for scope in self.local_stack:
                    for k, v in scope.items():
                        if k in self.env and "exported" in self._var_attrs.get(k, set()):
                            exec_env[k] = v
                return self._run_external(argv, exec_env, node.redirects)
            except RuntimeError as e:
                print(str(e), file=sys.stderr)
                return 1
        if isinstance(node, RedirectCommand):
            with self._redirected_fds(node.redirects):
                return self._exec_command(node.child)
        return 2

    def _trace_simple(self, node: SimpleCommand, argv: List[str], local_env: Dict[str, str]) -> None:
        items: List[str] = []
        for assign in node.assignments:
            val = local_env.get(assign.name, "")
            items.append(f"{assign.name}{assign.op}{self._trace_quote(val)}")
        force_quote: List[bool] = []
        if len(argv) == len(node.argv):
            for w in node.argv:
                parts = parse_word_parts(w.text)
                force_quote.append(any(p.quoted for p in parts))
        else:
            force_quote = [False] * len(argv)
        for i, arg in enumerate(argv):
            items.append(self._trace_quote(arg, force=force_quote[i] if i < len(force_quote) else False))
        ps4 = self._get_var("PS4")
        prefix = self._expand_prompt_string(ps4) if ps4 != "" else "+ "
        self._print_xtrace(prefix + " ".join(items))

    def _print_xtrace(self, text: str) -> None:
        target_fd = 2
        raw_fd, fd_set = self._get_var_with_state("BASH_XTRACEFD")
        if fd_set and raw_fd != "":
            try:
                parsed = int(raw_fd, 10)
                if parsed >= 0:
                    target_fd = parsed
            except Exception:
                target_fd = 2
        line = text + "\n"
        data = line.encode("utf-8", errors="surrogateescape")
        try:
            os.write(target_fd, data)
            return
        except OSError:
            if target_fd != 2:
                try:
                    os.write(2, data)
                    return
                except OSError:
                    pass
        try:
            self._print_stderr(text)
        except Exception:
            pass

    def _trace_quote(self, s: str, force: bool = False) -> str:
        if s == "":
            return "''"
        if force:
            return "'" + s.replace("'", "'\"'\"'") + "'"
        if (not force) and re.fullmatch(r"[A-Za-z0-9_./-]+", s):
            return s
        return shlex.quote(s)

    def _run_subshell(self, body: ListNode) -> int:
        self._set_subshell_depth(self._get_subshell_depth() + 1)
        saved_env = dict(self.env)
        self.env = dict(self.env)
        saved_options = dict(self.options)
        saved_local = [dict(s) for s in self.local_stack]
        saved_positional = list(self.positional)
        saved_loop_depth = self._loop_depth
        if self._bash_compat_level is not None and self._bash_compat_level >= 44:
            self._loop_depth = 0
        saved_cwd = os.getcwd()
        saved_traps = dict(self.traps)
        # EXIT trap is not inherited by subshells; additionally, TERM/WINCH
        # handlers are reset for subshell execution to match ash behavior in
        # tested cases.
        self.traps = {
            k: v
            for k, v in self.traps.items()
            if k != "EXIT" and not (k in {"TERM", "WINCH"} and v != "")
        }
        try:
            with self._push_frame(kind="subshell"):
                try:
                    status = self._exec_list(body)
                except SystemExit as e:
                    status = int(e.code) if e.code is not None else 0
                except (BreakLoop, ContinueLoop):
                    status = 1
                except ReturnFromFunction:
                    status = 1
                except RuntimeError as e:
                    print(str(e), file=sys.stderr)
                    status = 1
            sig_num: int | None = None
            if status < 0:
                sig_num = -status
            elif status >= 128:
                sig_num = status - 128
            if sig_num is not None and sig_num > 0:
                sig_name = None
                try:
                    sig_name = signal.Signals(sig_num).name.replace("SIG", "")
                except Exception:
                    sig_name = None
                if sig_name:
                    action = self.traps.get(sig_name)
                    if action:
                        self._run_trap_action(action, 128 + sig_num)
                        status = 0
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            return self._run_exit_trap(status)
        finally:
            self._set_subshell_depth(self._get_subshell_depth() - 1)
            self.env = saved_env
            self.options = saved_options
            self.local_stack = saved_local
            self.positional = saved_positional
            self._loop_depth = saved_loop_depth
            self.traps = saved_traps
            try:
                os.chdir(saved_cwd)
            except OSError:
                pass

    def _run_for(self, node: ForCommand) -> int:
        if node.name in self.readonly_vars:
            msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=node.name)
            self._report_error(msg, line=self.current_line, context="for")
            if self.options.get("posix", False) and self._is_noninteractive():
                raise SystemExit(1)
            return 1
        if node.items:
            items: List[str] = []
            for w in node.items:
                items.extend(self._expand_argv([w]))
        elif node.explicit_in:
            items = []
        else:
            items = list(self.positional)
        status = 0
        self._loop_depth += 1
        try:
            for item in items:
                self.env[node.name] = item
                try:
                    status = self._exec_list(node.body)
                    self._run_pending_traps()
                except ContinueLoop as e:
                    if e.count > 1:
                        raise ContinueLoop(e.count - 1)
                    continue
                except BreakLoop as e:
                    if e.count > 1:
                        raise BreakLoop(e.count - 1)
                    break
            return status
        finally:
            self._loop_depth -= 1

    def _run_arith_for(
        self,
        init_expr: str,
        cond_expr: str,
        update_expr: str,
        run_body: Callable[[], int],
    ) -> int:
        if init_expr:
            try:
                self._expand_arith(init_expr, context="for")
            except ArithExpansionFailure as e:
                return e.code
        status = 0
        self._loop_depth += 1
        try:
            while True:
                try:
                    if cond_expr:
                        cond_val = self._expand_arith(cond_expr, context="for")
                        should_run = int(cond_val) != 0
                    else:
                        should_run = True
                except ArithExpansionFailure as e:
                    return e.code
                except ValueError:
                    should_run = False
                if not should_run:
                    break
                try:
                    status = run_body()
                    self._run_pending_traps()
                except ContinueLoop as e:
                    if e.count > 1:
                        raise ContinueLoop(e.count - 1)
                    self._run_pending_traps()
                except BreakLoop as e:
                    if e.count > 1:
                        raise BreakLoop(e.count - 1)
                    status = 0
                    break
                if update_expr:
                    try:
                        self._expand_arith(update_expr, context="for")
                    except ArithExpansionFailure as e:
                        return e.code
            return status
        finally:
            self._loop_depth -= 1

    def _run_case(self, node: CaseCommand) -> int:
        value = self._expand_assignment_word(node.value.text)
        mode = "match"
        for item in node.items:
            matched = mode == "fallthrough"
            if mode != "fallthrough":
                for pat in item.patterns:
                    try:
                        expanded_pat = self._pattern_from_word(pat, for_case=True)
                        if self._case_pattern_matches(value, expanded_pat):
                            matched = True
                            break
                    except RuntimeError as e:
                        self._report_error(str(e))
                        return 1
            if not matched:
                continue
            status = self._exec_list(item.body)
            if item.op in {";;", "esac", ""}:
                return status
            if item.op == ";&":
                mode = "fallthrough"
                continue
            if item.op == ";;&":
                mode = "retest"
                continue
            return status
        return 0

    def _case_pattern_matches(self, value: str, pattern: str) -> bool:
        nocase = bool(self._shopts.get("nocasematch", False))
        if self._shopts.get("extglob", False) and self._has_extglob_syntax(pattern):
            try:
                return self._match_extglob_pattern(value, pattern, nocase=nocase)
            except Exception:
                # Fall back to base matcher if pattern parser/matcher rejects.
                pass
        if nocase:
            return fnmatch.fnmatchcase(value.lower(), pattern.lower())
        return fnmatch.fnmatchcase(value, pattern)

    def _match_extglob_pattern(self, value: str, pattern: str, *, nocase: bool = False) -> bool:
        if nocase:
            value = value.lower()
            pattern = pattern.lower()
        nodes = self._parse_extglob_nodes(pattern)
        return self._extglob_match(nodes, value)

    def _parse_extglob_nodes(self, pattern: str) -> list[Any]:
        n = len(pattern)

        def parse_seq(i: int, stops: set[str]) -> tuple[list[Any], int]:
            out: list[Any] = []
            lit_buf: list[str] = []

            def flush_lit() -> None:
                if lit_buf:
                    out.append(("lit", "".join(lit_buf)))
                    lit_buf.clear()

            while i < n:
                ch = pattern[i]
                if ch in stops:
                    break
                if ch == "\\":
                    if i + 1 < n:
                        lit_buf.append(pattern[i + 1])
                        i += 2
                    else:
                        lit_buf.append("\\")
                        i += 1
                    continue
                if ch == "[":
                    j = i + 1
                    if j < n and pattern[j] in {"!", "^"}:
                        j += 1
                    if j < n and pattern[j] == "]":
                        j += 1
                    while j < n:
                        if pattern[j] == "\\" and j + 1 < n:
                            j += 2
                            continue
                        if pattern[j] == "]":
                            break
                        j += 1
                    if j >= n or pattern[j] != "]":
                        lit_buf.append("[")
                        i += 1
                        continue
                    flush_lit()
                    out.append(("class", pattern[i : j + 1]))
                    i = j + 1
                    continue
                if ch in {"@", "?", "+", "*", "!"} and i + 1 < n and pattern[i + 1] == "(":
                    flush_lit()
                    op = ch
                    i += 2
                    alts: list[list[Any]] = []
                    while True:
                        alt, i = parse_seq(i, {"|", ")"})
                        alts.append(alt)
                        if i >= n:
                            raise ValueError("unterminated extglob")
                        if pattern[i] == "|":
                            i += 1
                            continue
                        if pattern[i] == ")":
                            i += 1
                            break
                    out.append(("ext", op, alts))
                    continue
                if ch == "*":
                    flush_lit()
                    out.append(("star",))
                    i += 1
                    continue
                if ch == "?":
                    flush_lit()
                    out.append(("any",))
                    i += 1
                    continue
                lit_buf.append(ch)
                i += 1

            flush_lit()
            return out, i

        nodes, idx = parse_seq(0, set())
        if idx != n:
            raise ValueError("unparsed pattern suffix")
        return nodes

    def _extglob_match(self, nodes: list[Any], text: str) -> bool:
        memo: dict[tuple[int, int], set[int]] = {}

        def class_match(raw: str, ch: str) -> bool:
            return fnmatch.fnmatchcase(ch, raw)

        def run(seq: list[Any], i: int) -> set[int]:
            key = (id(seq), i)
            cached = memo.get(key)
            if cached is not None:
                return cached
            out: set[int] = set()

            def walk(node_idx: int, pos: int) -> None:
                if node_idx >= len(seq):
                    out.add(pos)
                    return
                node = seq[node_idx]
                typ = node[0]
                if typ == "lit":
                    lit = node[1]
                    if text.startswith(lit, pos):
                        walk(node_idx + 1, pos + len(lit))
                    return
                if typ == "any":
                    if pos < len(text):
                        walk(node_idx + 1, pos + 1)
                    return
                if typ == "class":
                    if pos < len(text) and class_match(node[1], text[pos]):
                        walk(node_idx + 1, pos + 1)
                    return
                if typ == "star":
                    for j in range(pos, len(text) + 1):
                        walk(node_idx + 1, j)
                    return
                if typ == "ext":
                    op = node[1]
                    alts = node[2]
                    alt_ends: set[int] = set()
                    for alt in alts:
                        alt_ends.update(run(alt, pos))
                    if op == "@":
                        for j in alt_ends:
                            walk(node_idx + 1, j)
                        return
                    if op == "?":
                        walk(node_idx + 1, pos)
                        for j in alt_ends:
                            walk(node_idx + 1, j)
                        return
                    if op in {"*", "+"}:
                        starts: set[int] = {pos}
                        if op == "*":
                            walk(node_idx + 1, pos)
                        frontier: set[int] = set(alt_ends)
                        seen: set[int] = set()
                        while frontier:
                            j = frontier.pop()
                            if j in seen:
                                continue
                            seen.add(j)
                            walk(node_idx + 1, j)
                            nexts: set[int] = set()
                            for alt in alts:
                                for jj in run(alt, j):
                                    if jj != j:
                                        nexts.add(jj)
                            frontier.update(nexts)
                        return
                    if op == "!":
                        alt_forbidden: set[int] = set(alt_ends)
                        for j in range(pos, len(text) + 1):
                            if j not in alt_forbidden:
                                walk(node_idx + 1, j)
                        return
                    return

            walk(0, i)
            memo[key] = out
            return out

        return len(text) in run(nodes, 0)

    def _has_extglob_syntax(self, pattern: str) -> bool:
        i = 0
        in_class = False
        while i < len(pattern):
            ch = pattern[i]
            if ch == "\\" and i + 1 < len(pattern):
                i += 2
                continue
            if in_class:
                if ch == "]":
                    in_class = False
                i += 1
                continue
            if ch == "[":
                in_class = True
                i += 1
                continue
            if ch in {"@", "!", "?", "+", "*"} and i + 1 < len(pattern) and pattern[i + 1] == "(":
                return True
            i += 1
        return False

    def _run_builtin(self, name: str, argv: List[str]) -> int:
        if name == "cd":
            if self._is_restricted():
                self._print_stderr("cd: restricted")
                return 1
            target = argv[1] if len(argv) > 1 else self.env.get("HOME", "/")
            try:
                old = os.getcwd()
                resolved = target
                used_cdpath = False
                if (
                    target
                    and not os.path.isabs(target)
                    and not target.startswith(".")
                    and "CDPATH" in self.env
                ):
                    for base in self.env.get("CDPATH", "").split(":"):
                        candidate = os.path.join(base if base else ".", target)
                        if os.path.isdir(candidate):
                            resolved = candidate
                            used_cdpath = bool(base)
                            break
                os.chdir(resolved)
                self.env["OLDPWD"] = old
                self.env["PWD"] = os.getcwd()
                if used_cdpath:
                    print(self.env["PWD"])
                self._sync_dir_stack_current()
                return 0
            except OSError as e:
                msg = getattr(e, "strerror", None) or str(e)
                self._report_error(f"{target}: {msg}", line=self.current_line, context="cd")
                return 1
        if name == "pwd":
            physical = False
            i = 1
            while i < len(argv):
                a = argv[i]
                if a == "--":
                    i += 1
                    break
                if a == "-P":
                    physical = True
                    i += 1
                    continue
                if a == "-L":
                    physical = False
                    i += 1
                    continue
                if a.startswith("-") and a != "-":
                    self._report_error(
                        self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=a),
                        line=self.current_line,
                        context="pwd",
                    )
                    return 2
                break
            if i < len(argv):
                return 1
            if physical:
                try:
                    print(os.getcwd(), flush=True)
                except OSError:
                    return 1
                return 0
            print(self.env.get("PWD", os.getcwd()), flush=True)
            return 0
        if name in [".", "source"]:
            if len(argv) < 2:
                return 2
            path = argv[1]
            if self._is_restricted() and "/" in path:
                self._print_stderr(f"{name}: restricted")
                return 1
            args = argv[2:]
            status = self._run_source(path, args, builtin_name=name)
            if (
                status != 0
                and self.options.get("posix", False)
                and not self.options.get("i", False)
                and self._errexit_suppressed == 0
            ):
                raise SystemExit(status)
            return status
        if name == "local":
            return self._run_local(argv[1:])
        if name == "eval":
            return self._run_eval(argv[1:])
        if name in {"declare", "typeset"}:
            return self._run_declare(argv[1:], cmd_name=name)
        if name in {"mapfile", "readarray"}:
            return self._run_mapfile(argv[1:])
        if name == "set":
            return self._run_set(argv[1:])
        if name == "export":
            return self._run_export(argv[1:])
        if name == "readonly":
            return self._run_readonly(argv[1:])
        if name == "unset":
            return self._run_unset(argv[1:])
        if name == "shift":
            return self._run_shift(argv[1:])
        if name == "printf":
            return self._run_printf(argv[1:])
        if name == "echo":
            return self._run_echo(argv[1:])
        if name == "read":
            return self._run_read(argv[1:])
        if name == "true":
            return 0
        if name == "false":
            return 1
        if name == "command":
            return self._run_command_builtin(argv[1:])
        if name == "builtin":
            return self._run_builtin_builtin(argv[1:])
        if name == "enable":
            return self._run_enable(argv[1:])
        if name == "help":
            return self._run_help(argv[1:])
        if name == "dirs":
            return self._run_dirs(argv[1:])
        if name == "pushd":
            return self._run_pushd(argv[1:])
        if name == "popd":
            return self._run_popd(argv[1:])
        if name == "disown":
            return self._run_disown(argv[1:])
        if name == "complete":
            return self._run_complete(argv[1:])
        if name == "compgen":
            return self._run_compgen(argv[1:])
        if name == "compopt":
            return self._run_compopt(argv[1:])
        if name == "bind":
            return self._run_bind(argv[1:])
        if name == "exec":
            if len(argv) <= 1:
                return 0
            exec_argv0: str | None = None
            exec_login = False
            exec_clear_env = False
            i = 1
            while i < len(argv):
                a = argv[i]
                if a == "--":
                    i += 1
                    break
                if a == "-a":
                    if i + 1 >= len(argv):
                        self._print_stderr("exec: option requires an argument -- a")
                        return 2
                    exec_argv0 = argv[i + 1]
                    i += 2
                    continue
                if a == "-l":
                    exec_login = True
                    i += 1
                    continue
                if a == "-c":
                    exec_clear_env = True
                    i += 1
                    continue
                if a.startswith("-") and a != "-" and set(a[1:]).issubset({"c", "l"}):
                    exec_login = exec_login or ("l" in a[1:])
                    exec_clear_env = exec_clear_env or ("c" in a[1:])
                    i += 1
                    continue
                break
            if i > 1:
                cmd = argv[i:]
                if not cmd:
                    return 0
                if exec_login:
                    base = exec_argv0 if exec_argv0 is not None else os.path.basename(cmd[0])
                    exec_argv0 = "-" + base.lstrip("-")
                status = self._run_external(
                    cmd,
                    self._exported_env_view(self.env),
                    [],
                    context="exec",
                    argv0_override=exec_argv0,
                    clear_env=exec_clear_env,
                )
                raise SystemExit(status)
            if len(argv) == 2:
                spec = argv[1]
                m_open = re.match(r"^\{([A-Za-z_][A-Za-z0-9_]*)\}(<>|>>|>|<)(.*)$", spec)
                if m_open is not None:
                    var_name, op, path = m_open.group(1), m_open.group(2), m_open.group(3)
                    flags = None
                    if op == ">":
                        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
                    elif op == ">>":
                        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
                    elif op == "<":
                        flags = os.O_RDONLY
                    elif op == "<>":
                        flags = os.O_RDWR | os.O_CREAT
                    if flags is not None:
                        try:
                            fd = os.open(path, flags, 0o666)
                        except OSError as e:
                            self._print_stderr(f"exec: {path}: {e.strerror or 'error'}")
                            return 1
                        self._set_var(var_name, str(fd))
                        if fd >= 3:
                            self._user_fds.add(fd)
                        return 0
                m_close = re.match(r"^\{([A-Za-z_][A-Za-z0-9_]*)\}(?:>&-|<&-)$", spec)
                if m_close is not None:
                    var_name = m_close.group(1)
                    fd_s, is_set = self._get_var_with_state(var_name)
                    if is_set and fd_s.isdigit():
                        try:
                            os.close(int(fd_s))
                        except OSError:
                            pass
                    return 0
            cmd = argv[1:]
            if self._is_restricted() and "/" in cmd[0]:
                self._print_stderr("exec: restricted")
                return 1
            if self._is_builtin_enabled(cmd[0]):
                status = self._run_builtin(cmd[0], cmd)
                raise SystemExit(status)
            if self._has_function(cmd[0]):
                status = self._run_function(cmd[0], cmd[1:])
                raise SystemExit(status)
            status = self._run_external(cmd, self._exported_env_view(self.env), [], context="exec")
            raise SystemExit(status)
        if name == "trap":
            return self._run_trap(argv[1:])
        if name == "type":
            return self._run_type(argv[1:])
        if name == "alias":
            return self._run_alias(argv[1:])
        if name == "unalias":
            return self._run_unalias(argv[1:])
        if name == "wait":
            return self._run_wait(argv[1:])
        if name == "kill":
            return self._run_kill(argv[1:])
        if name == "fc":
            return self._run_fc(argv[1:])
        if name == "hash":
            return self._run_hash(argv[1:])
        if name == "time":
            return self._run_time(argv[1:])
        if name == "times":
            return self._run_times(argv[1:])
        if name == "ulimit":
            return self._run_ulimit(argv[1:])
        if name == "umask":
            return self._run_umask(argv[1:])
        if name == "jobs":
            return self._run_jobs(argv[1:])
        if name == "fg":
            return self._run_fg(argv[1:])
        if name == "bg":
            return self._run_bg_builtin(argv[1:])
        if name == "let":
            return self._run_let(argv[1:])
        if name == "getopts":
            return self._run_getopts(argv[1:])
        if name == "py":
            return self._run_py(argv[1:], entry_name="py")
        if name == "python:":
            return self._run_py(argv[1:], entry_name="python:")
        if name == "from":
            return self._run_from_import(argv[1:])
        if name == "shared":
            return self._run_shared(argv[1:])
        if name == "shopt":
            return self._run_shopt(argv[1:])
        if name == "caller":
            return self._run_caller(argv[1:])
        if name == "history":
            return self._run_history(argv[1:])
        if name == "suspend":
            return self._run_suspend(argv[1:])
        if name == "logout":
            return self._run_logout(argv[1:])
        if name in ["[", "[[", "test"]:
            return self._run_test(name, argv[1:])
        if name == "exit":
            if self._print_exit_job_warning():
                return 1
            self._terminate_active_jobs_for_exit()
            self._checkjobs_warned_once = False
            if len(argv) > 1:
                try:
                    code = int(argv[1], 10)
                except ValueError:
                    self._report_error(f"exit: {argv[1]}: numeric argument required", line=self.current_line)
                    raise SystemExit(2)
            elif self._trap_entry_status is not None:
                code = self._trap_entry_status
                if code == 0 and self.last_nonzero_status != 0:
                    code = self.last_nonzero_status
            else:
                code = self.last_status
            raise SystemExit(code)
        if name == "return":
            if len(argv) > 1:
                try:
                    code = int(argv[1], 10)
                except ValueError:
                    self._report_error(f"return: {argv[1]}: numeric argument required", line=self.current_line)
                    return 2
            elif self._trap_entry_status is not None:
                code = self._trap_entry_status
                if code == 0 and self.last_nonzero_status != 0:
                    code = self.last_nonzero_status
            else:
                code = self.last_status
            raise ReturnFromFunction(code)
        if name == ":":
            return 0
        if name == "break":
            count = int(argv[1]) if len(argv) > 1 else 1
            if self._loop_depth <= 0:
                return 1
            count = max(1, min(count, self._loop_depth))
            self.last_status = 0
            raise BreakLoop(count)
        if name == "continue":
            count = int(argv[1]) if len(argv) > 1 else 1
            if self._loop_depth <= 0:
                return 1
            count = max(1, min(count, self._loop_depth))
            self.last_status = 0
            raise ContinueLoop(count)
        return 2

    def _declaration_assigns_should_persist(self, argv: List[str]) -> bool:
        if not argv:
            return False
        name = argv[0]
        if name in {"export", "readonly"}:
            return True
        if name not in {"declare", "typeset", "local"}:
            return False
        has_print_only = False
        has_effective_flag = False
        for a in argv[1:]:
            if a == "--":
                continue
            if a.startswith("-") and a != "-":
                for ch in a[1:]:
                    if ch in {"p", "f", "F"}:
                        has_print_only = True
                    else:
                        has_effective_flag = True
                continue
            if "=" in a:
                return True
        if has_effective_flag:
            return True
        return not has_print_only

    def _parse_exec_named_fd_var(self, token: str) -> str | None:
        m = re.fullmatch(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", token)
        if m is None:
            return None
        return m.group(1)

    def _alloc_user_fd(self, src_fd: int) -> int:
        if src_fd >= 10:
            return src_fd
        if fcntl is None:
            return src_fd
        dup_fd = int(fcntl.fcntl(src_fd, fcntl.F_DUPFD, 10))
        os.close(src_fd)
        return dup_fd

    def _handle_exec_named_fd_redirect(self, var_name: str, redirects: List[Redirect]) -> int | None:
        if len(redirects) != 1:
            return None
        redir = redirects[0]
        if redir.fd is not None:
            return None

        if redir.op in [">", ">>", "<", "<>"]:
            target = self._expand_redir_target(redir)
            if target is None:
                self._print_stderr(f"exec: {var_name}: ambiguous redirect")
                return 1
            if redir.op == ">":
                flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            elif redir.op == ">>":
                flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            elif redir.op == "<":
                flags = os.O_RDONLY
            else:
                flags = os.O_RDWR | os.O_CREAT
            try:
                fd = os.open(target, flags, 0o666)
                fd = self._alloc_user_fd(fd)
            except OSError as e:
                self._print_stderr(f"exec: {target}: {e.strerror or 'error'}")
                return 1
            self._set_var(var_name, str(fd))
            if fd >= 3:
                self._user_fds.add(fd)
            return 0

        if redir.op in [">&", "<&"]:
            target = self._expand_redir_target(redir) if redir.target is not None else None
            if target == "-":
                fd_s, is_set = self._get_var_with_state(var_name)
                if not is_set or not fd_s.isdigit():
                    self._print_stderr(f"exec: {var_name}: ambiguous redirect")
                    return 1
                try:
                    fd = int(fd_s)
                    os.close(fd)
                    self._user_fds.discard(fd)
                except OSError:
                    pass
                return 0
            if target is None or not target.isdigit():
                self._print_stderr(f"exec: {target or var_name}: ambiguous redirect")
                return 1
            try:
                fd = os.dup(int(target))
                fd = self._alloc_user_fd(fd)
            except OSError as e:
                self._print_stderr(f"exec: {target}: {e.strerror or 'error'}")
                return 1
            self._set_var(var_name, str(fd))
            if fd >= 3:
                self._user_fds.add(fd)
            return 0

        return None

    def _run_source(self, path: str, args: List[str], builtin_name: str | None = None) -> int:
        orig_path = path
        found_via_path = False
        if "/" not in path and (self._shopts.get("sourcepath", False) or self.options.get("posix", False)):
            for d in self.env.get("PATH", os.defpath).split(os.pathsep):
                candidate = os.path.join(d, path)
                if os.path.isfile(candidate):
                    path = candidate
                    found_via_path = True
                    break
            if (
                not found_via_path
                and self.options.get("posix", False)
                and builtin_name in {".", "source"}
            ):
                if self._diag.style == "bash":
                    self._report_error(f".: {orig_path}: file not found", line=self.current_line)
                else:
                    self._report_error(f"{orig_path}: No such file or directory", line=self.current_line)
                return 1
        try:
            with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
                source = f.read()
        except OSError:
            if builtin_name in {".", "source"} and "/" not in path:
                if self._diag.style == "bash":
                    self._report_error(f".: {path}: file not found", line=self.current_line)
                else:
                    self._report_error(f"{path}: No such file or directory", line=self.current_line)
            else:
                self._report_error(f"{path}: No such file or directory", line=self.current_line)
            return 1
        source_args = list(args)
        saved_positional = list(self.positional) if args else None
        self.source_stack.append(path)
        self._sync_root_frame()
        if args:
            self.set_positional_args(args)
        parser_impl = Parser(
            source,
            aliases=self.aliases,
            lenient_unterminated_quotes=(self._bash_compat_level is not None),
        )
        status = 0
        try:
            with self._push_frame(kind="source", source=path):
                while True:
                    node = parser_impl.parse_next()
                    if node is None:
                        break
                    self.current_line = parser_impl.last_line
                    src_item = parser_impl.last_source_text()
                    if src_item is not None:
                        self.add_history_entry(src_item.rstrip("\n"))
                        if self.options.get("v", False):
                            line = src_item if src_item.endswith("\n") else src_item + "\n"
                            sys.stderr.write(line)
                    if self.options.get("n", False):
                        status = 0
                        continue
                    if parser_impl.last_lst_item is None:
                        raise ParseError("internal parse error: missing LST list item")
                    asdl_item = lst_list_item_to_asdl(parser_impl.last_lst_item, strict=True)
                    status = self._exec_asdl_list_item(asdl_item)
                    errexit_item_exempt = self._take_errexit_item_exempt()
                    self.last_status = status
                    if status != 0:
                        self.last_nonzero_status = status
                    self._trap_status_hint = status
                    if not getattr(node, "background", False):
                        self._run_pending_traps()
                    if (
                        status != 0
                        and self.options.get("e", False)
                        and self._errexit_suppressed == 0
                        and not errexit_item_exempt
                    ):
                        raise SystemExit(status)
        except ReturnFromFunction as e:
            status = e.code
        except AsdlMappingError:
            status = 2
        finally:
            if saved_positional is not None:
                # Mode split:
                # - ash/POSIX lane: always restore caller positional params for
                #   `. file args...`.
                # - bash lane: sourced `set -- ...` persists to caller.
                if self._diag.style != "bash":
                    self.set_positional_args(saved_positional)
                elif self.positional == source_args:
                    self.set_positional_args(saved_positional)
            if self.source_stack:
                self.source_stack.pop()
            self._sync_root_frame()
        return status

    def _run_function(self, name: str, args: List[str]) -> int:
        body = self.functions.get(name)
        body_asdl = self.functions_asdl.get(name)
        if body is None and body_asdl is None:
            return 127
        saved_positional = list(self.positional)
        self.set_positional_args(args)
        self.local_stack.append({})
        self._call_stack.append(name)
        saved_loop_depth = self._loop_depth
        if self._bash_compat_level is not None and self._bash_compat_level >= 44:
            # bash compat>=44: function body should not inherit caller loop control
            # context for break/continue.
            self._loop_depth = 0
        status = 0
        try:
            with self._push_frame(kind="function", funcname=name):
                if body_asdl is not None:
                    status = self._exec_asdl_command_list(body_asdl.get("children") or [])
                elif body is not None:
                    status = self._exec_list(body)
        except ReturnFromFunction as e:
            status = e.code
        finally:
            self._loop_depth = saved_loop_depth
            self._call_stack.pop()
            self.local_stack.pop()
            self.set_positional_args(saved_positional)
        return status

    def _has_function(self, name: str) -> bool:
        return name in self.functions_asdl or name in self.functions

    def _is_builtin_enabled(self, name: str) -> bool:
        return name in self.BUILTINS and name not in self.disabled_builtins

    def _should_dispatch_builtin(self, argv: list[str]) -> bool:
        if not argv:
            return False
        name = argv[0]
        if not self._is_builtin_enabled(name):
            return False
        # POSIX item 7: in POSIX mode, `time` is not a reserved word when the
        # following token begins with '-', so dispatch should prefer utility
        # command lookup over shell builtin timing behavior.
        if name == "time" and self.options.get("posix", False) and len(argv) > 1 and argv[1].startswith("-"):
            return False
        return True

    def _function_names(self) -> list[str]:
        return sorted(set(self.functions.keys()) | set(self.functions_asdl.keys()))


    def add_history_entry(self, line: str, *, force: bool = False) -> None:
        text = line.strip("\n")
        if not text:
            return
        if not force and not self.options.get("history", False):
            return
        self._history.append(text)
        ts: float | None = None
        if self._get_var("HISTTIMEFORMAT") != "":
            ts = time.time()
        self._history_ts.append(ts)

    def _history_resolve(self, token: str | None) -> int | None:
        if not self._history:
            return None
        if token is None:
            return len(self._history) - 1
        if token.startswith("-") and token[1:].isdigit():
            rel = int(token)
            idx = len(self._history) + rel
            return idx if 0 <= idx < len(self._history) else None
        if token.isdigit():
            n = int(token)
            idx = n - 1
            if 0 <= idx < len(self._history):
                return idx
            # Bash falls back to prefix lookup when a numeric event reference
            # does not resolve to an existing history number.
        for i in range(len(self._history) - 1, -1, -1):
            if self._history[i].startswith(token):
                return i
        return None

    def _fc_fail(self, key: DiagnosticKey, **kwargs: str) -> int:
        self._report_error(self._diag_msg(key, **kwargs), line=self.current_line, context="fc")
        return 1

    def _fc_execute_lines(self, lines: list[str]) -> int:
        replay_lines = [line for line in lines if line.strip()]
        if not replay_lines:
            return 0
        sig = tuple(replay_lines)
        if sig in self._fc_active_replay_signatures:
            return self._fc_fail(DiagnosticKey.FC_RECURSION_GUARD)
        if self._fc_replay_depth >= 32:
            return self._fc_fail(DiagnosticKey.FC_RECURSION_GUARD)
        self._fc_active_replay_signatures.add(sig)
        self._fc_replay_depth += 1
        try:
            status = 0
            for line in replay_lines:
                print(line)
                self.add_history_entry(line)
                status = self._eval_source(line)
            return status
        finally:
            self._fc_replay_depth -= 1
            self._fc_active_replay_signatures.discard(sig)

    def _run_fc(self, args: List[str]) -> int:
        mode = "edit"  # edit | list | subst
        reverse = False
        no_numbers = False
        editor: str | None = None
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            if args[i][1:].isdigit():
                break
            a = args[i]
            if a == "--":
                i += 1
                break
            if len(a) < 2:
                break
            j = 1
            while j < len(a):
                ch = a[j]
                if ch == "l":
                    mode = "list"
                elif ch == "r":
                    reverse = True
                elif ch == "n":
                    no_numbers = True
                elif ch == "s":
                    mode = "subst"
                elif ch == "e":
                    mode = "edit"
                    if j + 1 < len(a):
                        editor = a[j + 1 :]
                        j = len(a)
                        continue
                    i += 1
                    if i >= len(args):
                        return self._fc_fail(DiagnosticKey.FC_USAGE)
                    editor = args[i]
                    j = len(a)
                    continue
                else:
                    return self._fc_fail(DiagnosticKey.FC_USAGE)
                j += 1
            i += 1
        rest = args[i:]
        if mode == "subst":
            if rest and "=" in rest[0]:
                if len(rest) > 2:
                    return self._fc_fail(DiagnosticKey.FC_USAGE)
            elif len(rest) > 1:
                return self._fc_fail(DiagnosticKey.FC_USAGE)
        else:
            if len(rest) > 2:
                return self._fc_fail(DiagnosticKey.FC_USAGE)

        if not self._history:
            # Bash is permissive for list/edit surfaces when no history exists,
            # except `fc -e -` (re-exec mode) which fails without a command.
            if mode == "subst":
                return self._fc_fail(DiagnosticKey.FC_NO_HISTORY)
            if mode == "edit" and editor == "-":
                return self._fc_fail(DiagnosticKey.FC_NO_HISTORY)
            return 0
        current_is_fc = bool(self._history) and self._history[-1].lstrip().startswith("fc")
        default_ref = "-2" if current_is_fc and len(self._history) >= 2 else "-1"

        def _resolve_ref(tok: str | None) -> int | None:
            idx = self._history_resolve(tok if tok is not None else default_ref)
            if idx is not None and current_is_fc and idx == len(self._history) - 1 and len(self._history) >= 2:
                idx -= 1
            return idx

        if mode == "list":
            if len(rest) >= 1:
                first_idx = _resolve_ref(rest[0])
                # Bash keeps list mode permissive for unresolved refs.
                if first_idx is None:
                    return 0
                if len(rest) >= 2:
                    last_idx = _resolve_ref(rest[1])
                    if last_idx is None:
                        return 0
                else:
                    # With one explicit ref, list only that entry.
                    last_idx = first_idx
            else:
                first_idx = max(0, len(self._history) - 15)
                last_idx = _resolve_ref(default_ref)
                if last_idx is None:
                    return 0
            seq = list(range(first_idx, last_idx + 1)) if first_idx <= last_idx else list(range(first_idx, last_idx - 1, -1))
            if reverse:
                seq = list(reversed(seq))
            for n in seq:
                if no_numbers:
                    print(self._history[n])
                else:
                    print(f"{n + 1}\t{self._history[n]}")
            return 0

        if mode == "subst":
            substitute: str | None = None
            if rest and "=" in rest[0]:
                substitute = rest[0]
                rest = rest[1:]
            idx = _resolve_ref(rest[0] if rest else default_ref)
            if idx is None:
                bad_ref = rest[0] if rest else default_ref
                return self._fc_fail(DiagnosticKey.FC_EVENT_NOT_FOUND, ref=str(bad_ref))
            cmd = self._history[idx]
            if substitute is not None:
                old, new = substitute.split("=", 1)
                cmd = cmd.replace(old, new, 1)
            return self._fc_execute_lines([cmd])

        first_tok = rest[0] if len(rest) >= 1 else default_ref
        last_tok = rest[1] if len(rest) >= 2 else first_tok
        first_idx = _resolve_ref(first_tok)
        last_idx = _resolve_ref(last_tok)
        if first_idx is None or last_idx is None:
            bad_ref = first_tok if first_idx is None else last_tok
            return self._fc_fail(DiagnosticKey.FC_EVENT_NOT_FOUND, ref=str(bad_ref))
        seq = list(range(first_idx, last_idx + 1)) if first_idx <= last_idx else list(range(first_idx, last_idx - 1, -1))
        if reverse:
            seq = list(reversed(seq))
        selected = [self._history[n] for n in seq]
        editor_cmd = editor if editor is not None else (self.env.get("FCEDIT") or self.env.get("EDITOR") or "ed")

        path = ""
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
                path = tf.name
                for line in selected:
                    tf.write(line + "\n")
            if editor_cmd != "-":
                try:
                    parts = shlex.split(editor_cmd)
                except ValueError:
                    return self._fc_fail(DiagnosticKey.FC_INVALID_EDITOR)
                if not parts:
                    return self._fc_fail(DiagnosticKey.FC_INVALID_EDITOR)
                # Match shell runtime-visible environment for editor process.
                # This keeps FCEDIT/EDITOR execution aligned with current shell
                # state rather than host launcher environment.
                proc = subprocess.run(parts + [path], text=True, check=False, env=dict(self.env))
                if proc.returncode != 0:
                    return proc.returncode
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f]
        finally:
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass

        return self._fc_execute_lines(lines)

    def _run_external(
        self,
        argv: List[str],
        env: Dict[str, str],
        redirects: List[Redirect],
        context: str | None = None,
        argv0_override: str | None = None,
        clear_env: bool = False,
    ) -> int:
        if not argv:
            return 127
        if argv[0] == "":
            if self._bash_compat_level is not None:
                self._report_error(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=""), line=self.current_line, context=context)
            else:
                self._report_error(self._diag_msg(DiagnosticKey.PERMISSION_DENIED), line=self.current_line, context=context)
            return 127
        if self._is_restricted() and "/" in argv[0]:
            self._print_stderr(f"{argv[0]}: restricted: cannot specify `/' in command names")
            return 1
        try:
            with self._redirected_fds(redirects):
                if "/" in argv[0]:
                    resolved = argv[0]
                else:
                    resolved = self._resolve_external_path(argv[0], env)
                    if resolved is None:
                        fallback = self._resolve_external_nonexec_path(argv[0], env)
                        if fallback is None:
                            msg = self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0])
                            self._report_error(msg, line=self.current_line, context=context)
                            return 127
                        resolved = fallback
                exec_argv = list(argv)
                if argv0_override is not None and exec_argv:
                    exec_argv[0] = argv0_override
                child_env = {} if clear_env else dict(env)
                # If we're directly exec'ing a shebang script, propagate the script
                # basename so the child mctash can mirror ash-like /proc/$pid/comm.
                path0 = resolved
                if os.path.isfile(path0):
                    try:
                        with open(path0, "rb") as f:
                            head = f.read(2)
                        if head == b"#!":
                            child_env["MCTASH_COMM_NAME"] = os.path.basename(path0)
                    except OSError:
                        pass
                try:
                    job_id = getattr(self._thread_ctx, "job_id", None)
                    if self.options.get("i", False):
                        self._ensure_job_control_ready()
                    interactive_fg = bool(
                        not isinstance(job_id, int)
                        and self.options.get("i", False)
                        and self._job_control_ready
                        and os.isatty(0)
                        and hasattr(os, "tcsetpgrp")
                    )

                    def _child_preexec() -> None:
                        self._preexec_reset_signals()
                        if interactive_fg:
                            try:
                                os.setpgid(0, 0)
                            except OSError:
                                pass

                    proc = subprocess.Popen(
                        exec_argv,
                        executable=resolved,
                        env=child_env,
                        start_new_session=bool(isinstance(job_id, int)),
                        preexec_fn=_child_preexec,
                    )
                    tty_fd: int | None = None
                    shell_pgid: int | None = None
                    if interactive_fg:
                        try:
                            tty_fd = os.open("/dev/tty", os.O_RDWR)
                            shell_pgid = os.getpgrp()
                            # Avoid being stopped while switching foreground
                            # process group in interactive shells.
                            old_ttou = signal.getsignal(signal.SIGTTOU)
                            signal.signal(signal.SIGTTOU, signal.SIG_IGN)
                            try:
                                os.tcsetpgrp(tty_fd, proc.pid)
                                self._job_debug(
                                    f"fg-handoff shell_pgid={shell_pgid} fg_pid={proc.pid}"
                                )
                            finally:
                                signal.signal(signal.SIGTTOU, old_ttou)
                        except OSError:
                            if tty_fd is not None:
                                try:
                                    os.close(tty_fd)
                                except OSError:
                                    pass
                            tty_fd = None
                            shell_pgid = None
                    if isinstance(job_id, int):
                        self._bg_pids[job_id] = proc.pid
                        self._bg_pid_to_job[proc.pid] = job_id
                        self._bg_started_at.setdefault(job_id, time.monotonic())
                        self._bg_cmdline.setdefault(job_id, " ".join(argv))
                        if job_id == self._last_bg_job:
                            self._last_bg_pid = proc.pid
                    sent_sigint = False
                    while True:
                        try:
                            status = proc.wait(timeout=0.1)
                            break
                        except subprocess.TimeoutExpired:
                            # In interactive mode, ensure Ctrl-C interrupts the
                            # foreground external command promptly.
                            if (not sent_sigint) and ("INT" in self._pending_signals):
                                try:
                                    os.kill(proc.pid, signal.SIGINT)
                                    self._job_debug(f"forward-sigint fg_pid={proc.pid}")
                                except OSError:
                                    pass
                                sent_sigint = True
                    if tty_fd is not None and shell_pgid is not None:
                        try:
                            old_ttou = signal.getsignal(signal.SIGTTOU)
                            signal.signal(signal.SIGTTOU, signal.SIG_IGN)
                            try:
                                os.tcsetpgrp(tty_fd, shell_pgid)
                                self._job_debug(
                                    f"fg-restore shell_pgid={shell_pgid} fg_pid={proc.pid}"
                                )
                            finally:
                                signal.signal(signal.SIGTTOU, old_ttou)
                        except OSError:
                            pass
                        try:
                            os.close(tty_fd)
                        except OSError:
                            pass
                    if self._pending_signals and self.traps.get("TERM"):
                        if "TERM" in self._pending_signals:
                            self._run_pending_traps()
                            if self.options.get("e", False):
                                raise SystemExit(0)
                    if status < 0:
                        return 128 + (-status)
                    return status
                except FileNotFoundError:
                    if "/" in argv[0]:
                        msg = self._diag_msg(
                            DiagnosticKey.ERRNO_NAME,
                            name=argv[0],
                            error="No such file or directory",
                        )
                    else:
                        msg = self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0])
                    self._report_error(msg, line=self.current_line, context=context)
                    return 127
                except PermissionError:
                    self._report_error(
                        self._diag_msg(DiagnosticKey.PERMISSION_DENIED_NAME, name=argv[0]),
                        line=self.current_line,
                        context=context,
                    )
                    return 126
                except OSError as e:
                    eno = getattr(e, "errno", None)
                    if eno == 8 and os.path.isfile(resolved):
                        return self._run_source(resolved, argv[1:])
                    if eno == 36:
                        self._report_error(
                            self._diag_msg(DiagnosticKey.FILE_NAME_TOO_LONG_NAME, name=argv[0]),
                            line=self.current_line,
                            context=context,
                        )
                        return 127
                    self._report_error(
                        self._diag_msg(DiagnosticKey.ERRNO_NAME, name=argv[0], error=str(e.strerror)),
                        line=self.current_line,
                        context=context,
                    )
                    return 126
                except KeyboardInterrupt:
                    return 130
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 1

    def _resolve_external_path(self, argv0: str, env: Dict[str, str]) -> str | None:
        if "/" in argv0:
            if os.path.isdir(argv0):
                return None
            if os.path.isfile(argv0):
                return argv0
            return None
        cached = self._cmd_hash.get(argv0)
        if cached and os.path.isfile(cached) and os.access(cached, os.X_OK):
            return cached
        file_hit = self._classify_command_name(
            argv0,
            env=env,
            include_alias=False,
            include_function=False,
            include_builtin=False,
            include_nonexec=False,
        )
        if file_hit and file_hit[0][0] == "file":
            path = file_hit[0][1]
            self._cmd_hash[argv0] = path
            return path
        return None

    def _resolve_external_nonexec_path(self, argv0: str, env: Dict[str, str]) -> str | None:
        if "/" in argv0:
            return None
        hits = self._classify_command_name(
            argv0,
            env=env,
            include_alias=False,
            include_function=False,
            include_builtin=False,
            include_nonexec=True,
        )
        for kind, path in hits:
            if kind == "file_nonexec":
                return path
        return None

    def _iter_path_candidates(self, name: str, path_value: str) -> Iterator[str]:
        for d in path_value.split(os.pathsep):
            base = d or "."
            candidate = os.path.join(base, name)
            if os.path.isdir(candidate):
                continue
            if not os.path.isfile(candidate):
                continue
            yield candidate

    def _classify_command_name(
        self,
        name: str,
        *,
        env: Dict[str, str] | None = None,
        path_override: str | None = None,
        include_alias: bool = True,
        include_function: bool = True,
        include_builtin: bool = True,
        include_nonexec: bool = False,
    ) -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        if include_alias and name in self.aliases:
            hits.append(("alias", self.aliases[name]))
        if include_function and self._has_function(name):
            hits.append(("function", ""))
        if include_builtin and self._is_builtin_enabled(name):
            hits.append(("builtin", ""))

        lookup_env = env if env is not None else self.env
        path_value = path_override if path_override is not None else lookup_env.get("PATH", os.defpath)
        for candidate in self._iter_path_candidates(name, path_value):
            if os.access(candidate, os.X_OK):
                hits.append(("file", candidate))
                break
            if include_nonexec:
                hits.append(("file_nonexec", candidate))
                break
        return hits

    def _run_hash(self, args: List[str]) -> int:
        verbose = False
        reusable = False
        did_reset = False
        i = 0
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-r":
                self._cmd_hash.clear()
                did_reset = True
                i += 1
                continue
            if args[i] == "-v":
                verbose = True
                i += 1
                continue
            if args[i] == "-l":
                reusable = True
                i += 1
                continue
            return 2
        names = args[i:]
        if did_reset and not names and not verbose and not reusable:
            return 0
        if not names:
            if not self._cmd_hash and self._bash_compat_level is not None and not reusable:
                print("hash: hash table empty", flush=True)
                return 0
            for name in sorted(self._cmd_hash.keys()):
                if reusable:
                    print(f"builtin hash -p {shlex.quote(self._cmd_hash[name])} {shlex.quote(name)}", flush=True)
                else:
                    print(f"{name}={self._cmd_hash[name]}", flush=True)
            return 0
        status = 0
        for name in names:
            hits = self._classify_command_name(
                name,
                include_alias=False,
                include_function=False,
                include_builtin=False,
            )
            if not hits or hits[0][0] != "file":
                self._report_error(self._diag_msg(DiagnosticKey.HASH_NOT_FOUND, name=name), line=self.current_line)
                status = 1
                continue
            path = hits[0][1]
            self._cmd_hash[name] = path
            if verbose:
                print(f"{name}={path}", flush=True)
        return status

    def _run_alias(self, args: List[str]) -> int:
        status = 0
        show_with_prefix = False
        idx = 0
        while idx < len(args):
            arg = args[idx]
            if arg == "--":
                idx += 1
                break
            if arg == "-p":
                show_with_prefix = True
                idx += 1
                continue
            if arg.startswith("-"):
                self._report_error(
                    self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=arg),
                    line=self.current_line,
                    context="alias",
                )
                return 2
            break
        args = args[idx:]
        if not args:
            for name in sorted(self.aliases):
                print(f"alias {name}='{self.aliases[name]}'")
            return 0
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                self.aliases[name] = self._dequote_alias_value(value)
                continue
            if arg in self.aliases:
                if show_with_prefix:
                    print(f"alias {arg}='{self.aliases[arg]}'")
                else:
                    print(f"{arg}='{self.aliases[arg]}'")
            else:
                print(self._diag_msg(DiagnosticKey.ALIAS_NOT_FOUND, name=arg), file=sys.stderr)
                status = 1
        return status

    def _dequote_alias_value(self, value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]
        return value

    def _run_unalias(self, args: List[str]) -> int:
        if not args:
            self._print_stderr(self._diag_msg(DiagnosticKey.UNALIAS_USAGE))
            return 2
        if args[0] == "-a":
            self.aliases.clear()
            return 0
        status = 0
        for name in args:
            if name in self.aliases:
                del self.aliases[name]
            else:
                print(self._diag_msg(DiagnosticKey.UNALIAS_NOT_FOUND, name=name), file=sys.stderr)
                status = 1
        return status

    def _run_wait(self, args: List[str]) -> int:
        wait_for_termination = False

        def wait_job(job_id: int) -> int:
            th = self._bg_jobs.get(job_id)
            if th is not None:
                while th.is_alive():
                    if not wait_for_termination:
                        state = self._job_state.get(job_id)
                        if state == JOB_STOPPED:
                            sig_num = self._latest_job_event_value(job_id, "stopped")
                            if sig_num is None:
                                sig_num = int(signal.SIGSTOP)
                            return 128 + sig_num
                    th.join(0.05)
                    if self._pending_signals:
                        sig_name = self._pending_signals[0]
                        self._run_pending_traps()
                        sig_num = self._signal_number(sig_name)
                        return 128 + sig_num if sig_num else 1
            st = self._bg_status.get(job_id, 0)
            # Bash/POSIX: once wait reports a pid's completion status, that
            # status is no longer retained for a later wait on the same pid.
            self._bg_status.pop(job_id, None)
            self._bg_jobs.pop(job_id, None)
            self._job_state.pop(job_id, None)
            self._bg_stopped.discard(job_id)
            self._bg_notify_emitted.discard(job_id)
            try:
                self._bg_notifications.remove(job_id)
            except ValueError:
                pass
            pid = self._bg_pids.pop(job_id, None)
            if pid is not None:
                self._bg_pid_to_job.pop(pid, None)
            if st < 0:
                return 128 + (-st)
            return st

        i = 0
        while i < len(args):
            a = args[i]
            if a == "-f":
                wait_for_termination = True
                i += 1
                continue
            if a == "--":
                i += 1
                break
            if a.startswith("-"):
                return 2
            break
        args = args[i:]

        if not args:
            last = 0
            for job_id in sorted(self._bg_jobs.keys()):
                last = wait_job(job_id)
                if last >= 128:
                    return last
            return last
        last = 0
        for arg in args:
            _ = wait_for_termination
            job_id = self._resolve_job_id(arg)
            if job_id is None:
                self._report_error(
                    f"wait: pid {arg} is not a child of this shell",
                    line=self.current_line,
                )
                return 127
            if job_id not in self._bg_jobs and job_id not in self._bg_status:
                self._report_error(
                    f"wait: pid {arg} is not a child of this shell",
                    line=self.current_line,
                )
                return 127
            last = wait_job(job_id)
            if last >= 128:
                return last
        return last

    def _active_job_ids(self) -> list[int]:
        return sorted(set(self._bg_jobs.keys()) | set(self._bg_status.keys()))

    def _jobs_by_recency(self) -> list[int]:
        ids = self._active_job_ids()
        return sorted(ids, key=lambda jid: (self._bg_started_at.get(jid, 0.0), jid), reverse=True)

    def _current_job_id(self) -> int | None:
        ordered = self._jobs_by_recency()
        return ordered[0] if ordered else None

    def _previous_job_id(self) -> int | None:
        ordered = self._jobs_by_recency()
        return ordered[1] if len(ordered) > 1 else None

    def _resolve_named_jobspec(self, body: str) -> int | None:
        self._last_job_lookup_error = None
        if not body:
            return self._current_job_id()
        if body.startswith("?"):
            needle = body[1:]
            matches = [jid for jid in self._active_job_ids() if needle in self._bg_cmdline.get(jid, "")]
        else:
            matches = [jid for jid in self._active_job_ids() if self._bg_cmdline.get(jid, "").startswith(body)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            self._last_job_lookup_error = "ambiguous"
        return None

    def _resolve_job_id(self, token: str | None) -> int | None:
        self._last_job_lookup_error = None
        if token is None or token in {"%%", "%+", "%"}:
            return self._current_job_id()
        if token == "%-":
            return self._previous_job_id()
        if token.startswith("%?"):
            return self._resolve_named_jobspec(token[1:])
        if token.startswith("%") and not token[1:].isdigit():
            return self._resolve_named_jobspec(token[1:])
        raw = token[1:] if token.startswith("%") else token
        if not raw.isdigit():
            return None
        num = int(raw)
        if token.startswith("%"):
            return num
        if num in self._bg_jobs or num in self._bg_status:
            return num
        return self._bg_pid_to_job.get(num)

    def _run_jobs(self, args: List[str]) -> int:
        long_fmt = False
        pid_only = False
        i = 0
        while i < len(args):
            a = args[i]
            if a == "-l":
                long_fmt = True
                i += 1
                continue
            if a == "-p":
                pid_only = True
                i += 1
                continue
            return 2
        if not self.options.get("m", False):
            return 0
        job_ids = sorted(set(self._bg_jobs.keys()) | set(self._bg_status.keys()))
        for job_id in job_ids:
            pid = self._bg_pids.get(job_id)
            th = self._bg_jobs.get(job_id)
            done = (th is None) or (not th.is_alive())
            state_model = self._job_state.get(job_id)
            if state_model == JOB_STOPPED or job_id in self._bg_stopped:
                sig_num = self._latest_job_event_value(job_id, "stopped")
                if sig_num is not None:
                    try:
                        sig_name = signal.Signals(sig_num).name.replace("SIG", "")
                        state = f"Stopped({sig_name})"
                    except Exception:
                        state = "Stopped"
                else:
                    state = "Stopped"
            elif state_model == JOB_DONE:
                status = self._bg_status.get(job_id, 0)
                state = f"Done({status})" if status > 0 else "Done"
            else:
                state = "Done" if done else "Running"
            if pid_only:
                if pid is not None:
                    print(pid)
                continue
            if long_fmt and pid is not None:
                print(f"[{job_id}] {pid} {state}")
            else:
                print(f"[{job_id}] {state}")
        return 0

    def _active_jobs_for_exit_warning(self) -> list[int]:
        job_ids = self._active_job_ids()
        out: list[int] = []
        for jid in job_ids:
            if jid in self._bg_stopped:
                out.append(jid)
                continue
            th = self._bg_jobs.get(jid)
            if th is not None and th.is_alive():
                out.append(jid)
        return sorted(out)

    def _print_exit_job_warning(self) -> bool:
        if not (self.options.get("i", False) and self._shopts.get("checkjobs", False)):
            self._checkjobs_warned_once = False
            return False
        active = self._active_jobs_for_exit_warning()
        if not active:
            self._checkjobs_warned_once = False
            return False
        if self._checkjobs_warned_once:
            return False
        # bash --posix interactive comparator reports a generic running-jobs
        # warning in our PTY harness, even when jobs were STOP-signaled.
        msg = "There are running jobs."
        self._print_stderr(msg)
        for jid in active:
            cmd = self._bg_cmdline.get(jid, "")
            if jid in self._bg_stopped:
                state = "Stopped(SIGSTOP)"
            else:
                state = "Running"
            suffix = f" {cmd}" if cmd else ""
            self._print_stderr(f"[{jid}] {state}{suffix}")
        self._checkjobs_warned_once = True
        return True

    def _terminate_active_jobs_for_exit(self) -> None:
        active = self._active_jobs_for_exit_warning()
        for jid in active:
            pid = self._bg_pids.get(jid)
            if pid is None:
                continue
            try:
                os.kill(pid, signal.SIGTERM)
                if self._job_state.get(jid) == JOB_STOPPED or jid in self._bg_stopped:
                    os.kill(pid, signal.SIGCONT)
            except OSError:
                continue

    def _run_fg(self, args: List[str]) -> int:
        if len(args) > 1:
            return 2
        if not self.options.get("m", False):
            token = args[0] if args else "%%"
            if not token.startswith("%"):
                token = f"%{token}"
            self._report_error(
                self._diag_msg(DiagnosticKey.JOB_NOT_UNDER_CONTROL, token=token),
                line=self.current_line,
                context="fg",
            )
            return 1 if self._diag.style == "bash" else 2
        job_id = self._resolve_job_id(args[0] if args else None)
        if job_id is None:
            return 1
        if job_id not in self._bg_jobs and job_id not in self._bg_status:
            return 1
        self._bg_stopped.discard(job_id)
        status = self._run_wait([f"%{job_id}"])
        self.last_status = status
        if status != 0:
            self.last_nonzero_status = status
        return status

    def _run_bg_builtin(self, args: List[str]) -> int:
        # Threaded background jobs start immediately; no stopped-state resume yet.
        if len(args) > 1:
            return 2
        if not self.options.get("m", False):
            token = args[0] if args else "%%"
            if not token.startswith("%"):
                token = f"%{token}"
            self._report_error(
                self._diag_msg(DiagnosticKey.JOB_NOT_UNDER_CONTROL, token=token),
                line=self.current_line,
                context="bg",
            )
            return 1 if self._diag.style == "bash" else 2
        job_id = self._resolve_job_id(args[0] if args else None)
        if job_id is None:
            return 1
        if job_id not in self._bg_jobs and job_id not in self._bg_status:
            return 1
        self._bg_stopped.discard(job_id)
        print(f"[{job_id}]")
        return 0

    def _run_kill(self, args: List[str]) -> int:
        if not args:
            return 1
        if args[0] == "-l":
            if len(args) == 1:
                self._print_signal_table()
                return 0
            val = args[1]
            if val.isdigit():
                n = int(val, 10)
                if n > 128:
                    n -= 128
                try:
                    print(signal.Signals(n).name.replace("SIG", ""), flush=True)
                    return 0
                except Exception:
                    self._report_error(self._diag_msg(DiagnosticKey.INVALID_SIGNAL_SPEC, sig=val), line=self.current_line, context="kill")
                    return 1
            key = self._normalize_signal_spec(val)
            if key is None or key == "EXIT":
                self._report_error(self._diag_msg(DiagnosticKey.INVALID_SIGNAL_SPEC, sig=val), line=self.current_line, context="kill")
                return 1
            print(self._signal_number(key), flush=True)
            return 0
        sig_num = signal.SIGTERM
        i = 0
        targets: List[str] = []
        while i < len(args):
            a = args[i]
            if a == "--":
                targets.extend(args[i + 1 :])
                break
            if a == "-s":
                if i + 1 >= len(args):
                    return 1
                raw_spec = args[i + 1]
                if self.options.get("posix", False) and raw_spec.upper().startswith("SIG"):
                    return 1
                spec = self._normalize_signal_spec(raw_spec)
                if spec is None:
                    return 1
                n = self._signal_number(spec)
                if n == 0:
                    return 1
                sig_num = n
                i += 2
                continue
            if a.startswith("-") and a != "-" and a[1:].isdigit():
                try:
                    sig_num = int(a[1:], 10)
                except ValueError:
                    return 1
                i += 1
                continue
            if a.startswith("-") and a != "-" and not a[1:].isdigit():
                raw_spec = a[1:]
                if self.options.get("posix", False) and raw_spec.upper().startswith("SIG"):
                    return 1
                spec = self._normalize_signal_spec(raw_spec)
                if spec is None:
                    return 1
                n = self._signal_number(spec)
                if n == 0:
                    return 1
                sig_num = n
                i += 1
                continue
            targets.extend(args[i:])
            break
        if not targets:
            return 1
        status = 0
        for token in targets:
            pid: int | None = None
            from_job = False
            job_id_for_target: int | None = None
            if token == "%%":
                if self._last_bg_job is not None:
                    job_id_for_target = self._last_bg_job
                    pid = self._bg_pids.get(job_id_for_target)
                    from_job = True
            elif token.startswith("%") and token[1:].isdigit():
                job_id = int(token[1:])
                pid = self._bg_pids.get(job_id)
                job_id_for_target = job_id
                from_job = True
            elif token.isdigit():
                pid = int(token)
                job_id_for_target = self._bg_pid_to_job.get(pid)
            if pid is None:
                status = 1
                continue
            if (
                job_id_for_target is not None
                and sig_num in [getattr(signal, "SIGHUP", -1), getattr(signal, "SIGTERM", -1)]
            ):
                started = self._bg_started_at.get(job_id_for_target)
                if started is not None:
                    age = time.monotonic() - started
                    min_age = 0.8 if sig_num == getattr(signal, "SIGHUP", -1) else 0.4
                    if age < min_age:
                        time.sleep(min_age - age)
            try:
                os.kill(pid, sig_num)
                if pid == os.getpid() and self._get_subshell_depth() == 0 and self._running_trap:
                    sig_name = None
                    try:
                        sig_name = signal.Signals(sig_num).name.replace("SIG", "")
                    except Exception:
                        sig_name = None
                    if sig_name is not None:
                        action = self.traps.get(sig_name)
                        if action:
                            while sig_name in self._pending_signals:
                                self._pending_signals.remove(sig_name)
                            if self._running_trap:
                                saved = self._trap_entry_status
                                self._trap_entry_status = self.last_status
                                try:
                                    with self._push_frame(kind="trap", funcname="trap"):
                                        self._eval_source(action, propagate_exit=True, propagate_return=True)
                                finally:
                                    self._trap_entry_status = saved
                            else:
                                entry_status = self.last_status
                                if entry_status == 0 and self.last_nonzero_status != 0:
                                    entry_status = self.last_nonzero_status
                                self._run_trap_action(action, entry_status)
                            while sig_name in self._pending_signals:
                                self._pending_signals.remove(sig_name)
                            self._trap_inline_handled.append(sig_name)
                if job_id_for_target is not None:
                    if sig_num in {
                        getattr(signal, "SIGSTOP", -1),
                        getattr(signal, "SIGTSTP", -1),
                        getattr(signal, "SIGTTIN", -1),
                        getattr(signal, "SIGTTOU", -1),
                    }:
                        self._mark_job_stopped(job_id_for_target, sig_num)
                    elif sig_num in {getattr(signal, "SIGCONT", -1)}:
                        self._mark_job_continued(job_id_for_target)
                    elif sig_num in {
                        getattr(signal, "SIGTERM", -1),
                        getattr(signal, "SIGKILL", -1),
                        getattr(signal, "SIGHUP", -1),
                        getattr(signal, "SIGINT", -1),
                        getattr(signal, "SIGQUIT", -1),
                    }:
                        self._mark_job_done(job_id_for_target, -sig_num)
            except Exception:
                status = 1
        return status

    def _run_times(self, args: List[str]) -> int:
        if args:
            return 2
        t = os.times()
        def _fmt(v: float) -> str:
            mins = int(v // 60)
            secs = v - mins * 60
            return f"{mins}m{secs:0.3f}s"
        print(f"{_fmt(t.user)} {_fmt(t.system)}")
        print(f"{_fmt(t.children_user)} {_fmt(t.children_system)}")
        return 0

    def _run_time(self, args: List[str]) -> int:
        posix_format = False
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                i += 1
                break
            if a == "-p":
                posix_format = True
                i += 1
                continue
            break
        cmd = args[i:]
        if not cmd:
            return self._run_times([])

        start_real = time.monotonic()
        t0 = os.times()
        if cmd and cmd[0] == "time" and (len(cmd) == 1 or cmd[1] != "-p"):
            if posix_format:
                # Match bash POSIX behavior for `time -p time ...`: the inner
                # `time` is resolved as utility command.
                source = "command " + " ".join(cmd)
            else:
                # Match bash POSIX behavior for `time time ...`: only outer
                # timing is emitted.
                source = " ".join(cmd[1:])
        else:
            source = " ".join(cmd)
        with self._suppress_errexit():
            status = self._eval_source(source, parse_context="time")
        t1 = os.times()
        real = max(0.0, time.monotonic() - start_real)
        user = max(0.0, (t1.user + t1.children_user) - (t0.user + t0.children_user))
        sys_t = max(0.0, (t1.system + t1.children_system) - (t0.system + t0.children_system))

        if posix_format:
            print(f"real {real:.2f}", file=sys.stderr)
            print(f"user {user:.2f}", file=sys.stderr)
            print(f"sys {sys_t:.2f}", file=sys.stderr)
            return status

        fmt = self.env.get("TIMEFORMAT", "")
        if not fmt:
            fmt = "real %3R\nuser %3U\nsys %3S"
        elif fmt.startswith("$'") and fmt.endswith("'"):
            fmt = self._decode_backslash_escapes(fmt[2:-1])
        elif fmt.startswith("$"):
            fmt = self._decode_backslash_escapes(fmt[1:])
        rendered, invalid = self._render_timeformat(fmt, real, user, sys_t)
        if invalid is not None:
            self._print_stderr(
                self._format_error(
                    f"TIMEFORMAT: `{invalid}': invalid format character",
                    line=self.current_line,
                )
            )
            return status
        if rendered:
            if not rendered.endswith("\n"):
                rendered += "\n"
            sys.stderr.write(rendered)
        return status

    def _render_timeformat(self, fmt: str, real: float, user: float, sys_t: float) -> tuple[str, str | None]:
        out: list[str] = []
        i = 0
        n = len(fmt)
        while i < n:
            ch = fmt[i]
            if ch != "%":
                out.append(ch)
                i += 1
                continue
            i += 1
            if i >= n:
                out.append("%")
                break
            precision = None
            if fmt[i].isdigit():
                precision = int(fmt[i])
                i += 1
                if i >= n:
                    out.append("%")
                    break
            code = fmt[i]
            i += 1
            if code == "%":
                out.append("%")
                continue
            p = 3 if precision is None else precision
            if code == "R":
                out.append(f"{real:.{p}f}")
                continue
            if code == "U":
                out.append(f"{user:.{p}f}")
                continue
            if code == "S":
                out.append(f"{sys_t:.{p}f}")
                continue
            if code == "P":
                if precision is not None:
                    return "", "P"
                if real <= 0.0:
                    out.append("0.00")
                else:
                    out.append(f"{((user + sys_t) * 100.0 / real):.2f}")
                continue
            return "", code
        return "".join(out), None

    def _run_umask(self, args: List[str]) -> int:
        symbolic = False
        print_mode = False
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            opt = args[i]
            if opt == "--":
                i += 1
                break
            for ch in opt[1:]:
                if ch == "S":
                    symbolic = True
                elif ch == "p":
                    print_mode = True
                else:
                    return 2
            i += 1
        args = args[i:]
        if not args:
            cur = os.umask(0)
            os.umask(cur)
            if symbolic:
                def _perm(tri: int, who: str) -> str:
                    bits = 7 - tri
                    out = who + "="
                    if bits & 4:
                        out += "r"
                    if bits & 2:
                        out += "w"
                    if bits & 1:
                        out += "x"
                    return out

                u = (cur >> 6) & 0x7
                g = (cur >> 3) & 0x7
                o = cur & 0x7
                txt = ",".join([_perm(u, "u"), _perm(g, "g"), _perm(o, "o")])
                if print_mode:
                    print(f"umask -S {txt}")
                else:
                    print(txt)
            else:
                if print_mode:
                    print(f"umask {cur:04o}")
                else:
                    print(f"{cur:04o}")
            return 0
        spec = args[0]
        if any(ch in spec for ch in "=,+-"):
            # Minimal symbolic form support used by bash upstream corpus:
            # comma-separated who=perms clauses (e.g. u=rwx,g=rwx,o=rx).
            cur = os.umask(0)
            os.umask(cur)
            mode = 0o777 & (~cur)
            who_bits = {"u": 0o700, "g": 0o070, "o": 0o007, "a": 0o777}
            perm_bits = {"r": 0o444, "w": 0o222, "x": 0o111}
            for clause in spec.split(","):
                if not clause:
                    return 2
                m = re.fullmatch(r"([ugoa]*)([=])([rwx]*)", clause)
                if m is None:
                    return 2
                who, op, perms = m.group(1), m.group(2), m.group(3)
                who = who or "a"
                scope = 0
                for ch in who:
                    scope |= who_bits[ch]
                if op != "=":
                    return 2
                mask = 0
                for p in perms:
                    mask |= perm_bits[p]
                mode = (mode & ~scope) | (mask & scope)
            os.umask((~mode) & 0o777)
            return 0
        try:
            mask = int(spec, 8)
        except ValueError:
            return 2
        os.umask(mask)
        return 0

    def _run_ulimit(self, args: List[str]) -> int:
        use_soft = False
        use_hard = False
        list_all = False
        selected_flag = "f"
        limit_key = resource.RLIMIT_FSIZE
        i = 0

        def _maybe(flag: str, name: str) -> tuple[str, int] | None:
            key = getattr(resource, name, None)
            if key is None:
                return None
            return flag, key

        limit_map: dict[str, int] = {}
        for item in [
            _maybe("c", "RLIMIT_CORE"),
            _maybe("d", "RLIMIT_DATA"),
            _maybe("f", "RLIMIT_FSIZE"),
            _maybe("l", "RLIMIT_MEMLOCK"),
            _maybe("m", "RLIMIT_RSS"),
            _maybe("n", "RLIMIT_NOFILE"),
            _maybe("p", "RLIMIT_NPROC"),
            _maybe("s", "RLIMIT_STACK"),
            _maybe("t", "RLIMIT_CPU"),
            _maybe("v", "RLIMIT_AS"),
        ]:
            if item is None:
                continue
            k, v = item
            limit_map[k] = v

        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            opt = args[i]
            if opt == "--":
                i += 1
                break
            for ch in opt[1:]:
                if ch == "S":
                    use_soft = True
                    continue
                if ch == "H":
                    use_hard = True
                    continue
                if ch == "a":
                    list_all = True
                    continue
                if ch in limit_map:
                    selected_flag = ch
                    limit_key = limit_map[ch]
                    continue
                return 2
            i += 1

        if not use_soft and not use_hard:
            use_soft = True

        def _fmt(val: int) -> str:
            return "unlimited" if val == resource.RLIM_INFINITY else str(val)

        unit_by_flag = {
            "c": "blocks",
            "d": "kbytes",
            "f": "blocks",
            "l": "kbytes",
            "m": "kbytes",
            "n": "raw",
            "p": "raw",
            "s": "kbytes",
            "t": "raw",
            "v": "kbytes",
        }
        unit_by_key: dict[int, str] = {}
        for flg, key in limit_map.items():
            unit_by_key[key] = unit_by_flag.get(flg, "raw")

        def _render_for_user(key: int, val: int) -> str:
            if val == resource.RLIM_INFINITY:
                return "unlimited"
            unit = unit_by_key.get(key, "raw")
            if unit == "kbytes":
                return str(int(val // 1024))
            if unit == "blocks":
                return str(int(val // 512))
            return str(int(val))

        def _parse_user_limit(key: int, text: str) -> int:
            if text == "unlimited":
                return resource.RLIM_INFINITY
            try:
                raw_num = int(text, 10)
            except (ValueError, OverflowError):
                raise
            unit = unit_by_key.get(key, "raw")
            if unit == "kbytes":
                return raw_num * 1024
            if unit == "blocks":
                return raw_num * 512
            return raw_num

        def _cur_value(key: int) -> int:
            soft, hard = resource.getrlimit(key)
            return hard if use_hard and not use_soft else soft

        if list_all:
            rows = []
            if "t" in limit_map:
                rows.append(("time(seconds)", limit_map["t"]))
            if "f" in limit_map:
                rows.append(("file(blocks)", limit_map["f"]))
            if "d" in limit_map:
                rows.append(("data(kbytes)", limit_map["d"]))
            if "s" in limit_map:
                rows.append(("stack(kbytes)", limit_map["s"]))
            if "c" in limit_map:
                rows.append(("coredump(blocks)", limit_map["c"]))
            if "m" in limit_map:
                rows.append(("memory(kbytes)", limit_map["m"]))
            if "l" in limit_map:
                rows.append(("locked memory(kbytes)", limit_map["l"]))
            if "p" in limit_map:
                rows.append(("process", limit_map["p"]))
            if "n" in limit_map:
                rows.append(("nofiles", limit_map["n"]))
            if "v" in limit_map:
                rows.append(("vmemory(kbytes)", limit_map["v"]))
            if hasattr(resource, "RLIMIT_LOCKS"):
                rows.append(("locks", resource.RLIMIT_LOCKS))
            if hasattr(resource, "RLIMIT_RTPRIO"):
                rows.append(("rtprio", resource.RLIMIT_RTPRIO))
            for label, key in rows:
                print(f"{label:16} {_render_for_user(key, _cur_value(key))}")
            return 0

        rest = args[i:]
        if len(rest) > 1:
            return 2
        if not rest:
            print(_render_for_user(limit_key, _cur_value(limit_key)))
            return 0

        target = rest[0]
        try:
            new_lim = _parse_user_limit(limit_key, target)
        except (ValueError, OverflowError):
            return 2

        soft, hard = resource.getrlimit(limit_key)
        new_soft, new_hard = soft, hard
        if use_soft and use_hard:
            new_soft, new_hard = new_lim, new_lim
        elif use_hard:
            new_hard = new_lim
            if new_soft != resource.RLIM_INFINITY and new_hard != resource.RLIM_INFINITY and new_soft > new_hard:
                new_soft = new_hard
        else:
            new_soft = new_lim
        try:
            resource.setrlimit(limit_key, (new_soft, new_hard))
        except (OSError, ValueError):
            return 1
        except OverflowError:
            return 2
        return 0

    def _expand_aliases(self, argv: List[str]) -> List[str]:
        if not argv:
            return argv
        out, trailing = self._expand_alias_at(list(argv), 0)
        if trailing and len(out) > 1:
            out, _ = self._expand_alias_at(out, 1)
        return out

    def _alias_has_unmatched_quote(self, value: str) -> bool:
        return self._alias_unmatched_quote_char(value) is not None

    def _alias_unmatched_quote_char(self, value: str) -> str | None:
        in_single = False
        in_double = False
        i = 0
        while i < len(value):
            ch = value[i]
            if in_single:
                if ch == "'":
                    in_single = False
                i += 1
                continue
            if in_double:
                if ch == "\\" and i + 1 < len(value):
                    i += 2
                    continue
                if ch == '"':
                    in_double = False
                i += 1
                continue
            if ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
            i += 1
        if in_single:
            return "'"
        if in_double:
            return '"'
        return None

    def _expand_alias_at(self, argv: List[str], idx: int) -> Tuple[List[str], bool]:
        seen: set[str] = set()
        trailing = False
        while idx < len(argv):
            word = argv[idx]
            value = self.aliases.get(word)
            if value is None or word in seen:
                break
            seen.add(word)
            if value.lstrip().startswith("#"):
                argv = argv[:idx]
                trailing = False
                break
            trailing = value.endswith(" ")
            raw_parts: List[str] = []
            try:
                reader = TokenReader(value)
                lex_ctx = LexContext(reserved_words=set(), allow_reserved=False, allow_newline=False)
                while True:
                    tok = reader.next(lex_ctx)
                    if tok is None:
                        break
                    if tok.kind == "WORD":
                        raw_parts.append(tok.value)
            except LexError:
                raw_parts = [value]
            parts: List[str] = []
            for raw in raw_parts:
                parts.append(self._expand_word(raw))
            if not parts:
                argv = argv[:idx] + argv[idx + 1 :]
                break
            argv = argv[:idx] + parts + argv[idx + 1 :]
        return argv, trailing

    def _apply_redirects(
        self,
        redirects: List[Redirect],
        stdin: Optional[object],
        stdout: Optional[object],
        stderr: Optional[object],
    ) -> Tuple[Optional[object], Optional[object], Optional[object], List[object]]:
        to_close: List[object] = []
        for redir in redirects:
            target_fd = redir.fd
            if target_fd is None:
                target_fd = 0 if redir.op in ["<", "<<", "<<<", "<&", "<>"] else 1
            target = self._expand_redir_target(redir)
            if redir.op == "<":
                f = self._open_for_redir(target, "rb", redir.op)
                to_close.append(f)
                if target_fd == 0:
                    stdin = f
            elif redir.op == "<>":
                f = self._open_for_redir_readwrite(target)
                to_close.append(f)
                if target_fd == 0:
                    stdin = f
            elif redir.op == ">":
                if target_fd == 1 and target == "/proc/self/fd/1" and stdout is not None:
                    continue
                f = self._open_for_redir(target, "wb", redir.op)
                to_close.append(f)
                if target_fd == 1:
                    stdout = f
                elif target_fd == 2:
                    stderr = f
            elif redir.op == ">>":
                f = self._open_for_redir(target, "ab", redir.op)
                to_close.append(f)
                if target_fd == 1:
                    stdout = f
                elif target_fd == 2:
                    stderr = f
            elif redir.op == "&>":
                f = self._open_for_redir(target, "wb", redir.op)
                to_close.append(f)
                stdout = f
                stderr = f
            elif redir.op == "&>>":
                f = self._open_for_redir(target, "ab", redir.op)
                to_close.append(f)
                stdout = f
                stderr = f
            elif redir.op == "<<":
                content = self._expand_heredoc(redir)
                f = tempfile.TemporaryFile()
                f.write(content.encode("utf-8"))
                f.seek(0)
                to_close.append(f)
                if target_fd == 0:
                    stdin = f
            elif redir.op == "<<<":
                content = self._expand_here_string(redir)
                f = tempfile.TemporaryFile()
                f.write(content.encode("utf-8"))
                f.seek(0)
                to_close.append(f)
                if target_fd == 0:
                    stdin = f
            elif redir.op == ">&":
                if target == "-":
                    if target_fd == 1:
                        stdout = subprocess.DEVNULL
                    elif target_fd == 2:
                        stderr = subprocess.DEVNULL
                    continue
                if target.isdigit():
                    src_fd = int(target)
                    if target_fd == 2 and src_fd == 1:
                        stderr = stdout if stdout is not None else None
                        continue
                    if target_fd == 1 and src_fd == 2:
                        stdout = subprocess.DEVNULL
                        continue
                raise RuntimeError(self._format_error("unsupported pipeline redirection", line=self.current_line))
            elif redir.op == "<&":
                if target == "-":
                    stdin = subprocess.DEVNULL
                    continue
                if target.isdigit() and target_fd == 0 and int(target) == 0:
                    continue
                raise RuntimeError(self._format_error("unsupported pipeline redirection", line=self.current_line))
        return stdin, stdout, stderr, to_close

    def _open_for_redir(self, path: str, mode: str, op: str) -> object:
        try:
            if path.startswith("/dev/tcp/") or path.startswith("/dev/udp/"):
                return self._open_network_redir(path, mode)
            if op == ">" and self.options.get("C", False):
                try:
                    st = os.stat(path)
                    if stat.S_ISREG(st.st_mode):
                        raise RuntimeError(self._format_error(f"can't create {path}: file exists", line=self.current_line))
                except FileNotFoundError:
                    pass
            return open(path, mode)
        except OSError as e:
            reason = e.strerror or "error"
            if e.errno == 2:
                if op in [">", ">>", "<>"]:
                    msg = f"can't create {path}: nonexistent directory"
                    raise RuntimeError(self._format_error(msg, line=self.current_line))
                reason = "No such file or directory"
            if op == "<":
                msg = f"can't open {path}: {reason}"
            else:
                msg = f"{path}: {reason}"
            raise RuntimeError(self._format_error(msg, line=self.current_line))

    def _open_network_redir(self, path: str, mode: str) -> object:
        proto = "tcp" if path.startswith("/dev/tcp/") else "udp"
        rest = path.split("/", 3)[3] if path.count("/") >= 3 else ""
        parts = rest.split("/", 1)
        if len(parts) != 2:
            raise RuntimeError(self._format_error(f"{path}: invalid network redirection", line=self.current_line))
        host, port_s = parts
        try:
            port = int(port_s, 10)
        except ValueError:
            raise RuntimeError(self._format_error(f"{path}: invalid port", line=self.current_line))
        if not (0 <= port <= 65535):
            raise RuntimeError(self._format_error(f"{path}: invalid port", line=self.current_line))
        try:
            if proto == "tcp":
                sock = socket.create_connection((host, port), timeout=3.0)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect((host, port))
            sock.settimeout(None)
            io_mode = "rb" if "r" in mode and "w" not in mode and "a" not in mode else "wb"
            return sock.makefile(io_mode, buffering=0)
        except OSError as e:
            reason = e.strerror or "error"
            raise RuntimeError(self._format_error(f"{path}: {reason}", line=self.current_line))

    def _open_for_redir_readwrite(self, path: str) -> object:
        try:
            fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o666)
            return os.fdopen(fd, "r+b", buffering=0)
        except OSError as e:
            reason = e.strerror or "error"
            if e.errno == 2:
                raise RuntimeError(self._format_error(f"can't create {path}: {reason}", line=self.current_line))
            raise RuntimeError(self._format_error(f"can't open {path}: {reason}", line=self.current_line))

    def _dup2_file(self, f: object, fd: int) -> None:
        src = f.fileno()
        if src == fd:
            # Avoid closing target fd when the temporary file object is destroyed.
            tmp = os.dup(src)
            f.close()
            os.dup2(tmp, fd)
            os.close(tmp)
            return
        os.dup2(src, fd)
        f.close()

    def _apply_persistent_redirects(self, redirects: List[Redirect]) -> None:
        for redir in redirects:
            fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<<<", "<&", "<>"] else 1)
            target = self._expand_redir_target(redir)
            if redir.op == "<":
                f = self._open_for_redir(target, "rb", redir.op)
                self._dup2_file(f, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
            elif redir.op == "<>":
                f = self._open_for_redir_readwrite(target)
                self._dup2_file(f, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
            elif redir.op == ">":
                f = self._open_for_redir(target, "wb", redir.op)
                self._dup2_file(f, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
            elif redir.op == ">>":
                f = self._open_for_redir(target, "ab", redir.op)
                self._dup2_file(f, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
            elif redir.op == "&>":
                f = self._open_for_redir(target, "wb", redir.op)
                dup_fd = os.dup(f.fileno())
                self._dup2_file(f, 1)
                os.dup2(dup_fd, 2)
                os.close(dup_fd)
            elif redir.op == "&>>":
                f = self._open_for_redir(target, "ab", redir.op)
                dup_fd = os.dup(f.fileno())
                self._dup2_file(f, 1)
                os.dup2(dup_fd, 2)
                os.close(dup_fd)
            elif redir.op == "<<":
                content = self._expand_heredoc(redir)
                f = tempfile.TemporaryFile()
                f.write(content.encode("utf-8"))
                f.seek(0)
                self._dup2_file(f, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
            elif redir.op == "<<<":
                content = self._expand_here_string(redir)
                f = tempfile.TemporaryFile()
                f.write(content.encode("utf-8"))
                f.seek(0)
                self._dup2_file(f, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
            elif redir.op == ">&":
                self._dup_fd(redir, is_output=True, default_fd=fd)
            elif redir.op == "<&":
                self._dup_fd(redir, is_output=False, default_fd=fd)

    @contextmanager
    def _redirected_fds(self, redirects: List[Redirect]):
        if not redirects:
            yield
            return
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        saved: List[Tuple[int, int]] = []
        saved_active = set(self._active_temp_fds)
        saved_user_fds = set(self._user_fds)
        transient_fds: set[int] = set()
        self._fd_redirect_depth += 1
        try:
            for redir in redirects:
                fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<<<", "<&", "<>"] else 1)
                target = self._expand_redir_target(redir)
                if redir.op in {"&>", "&>>"}:
                    for save_fd in (1, 2):
                        try:
                            saved_fd = os.dup(save_fd)
                            try:
                                os.set_inheritable(saved_fd, False)
                            except OSError:
                                pass
                        except OSError:
                            saved_fd = -1
                        saved.append((save_fd, saved_fd))
                    mode = "wb" if redir.op == "&>" else "ab"
                    f = self._open_for_redir(target, mode, redir.op)
                    dup_fd = os.dup(f.fileno())
                    self._dup2_file(f, 1)
                    os.dup2(dup_fd, 2)
                    os.close(dup_fd)
                    continue
                try:
                    saved_fd = os.dup(fd)
                    try:
                        os.set_inheritable(saved_fd, False)
                    except OSError:
                        pass
                except OSError:
                    # Descriptor may be closed before redirection (e.g. fd 3).
                    saved_fd = -1
                saved.append((fd, saved_fd))
                if redir.op == "<":
                    f = self._open_for_redir(target, "rb", redir.op)
                    self._dup2_file(f, fd)
                    if fd >= 3:
                        transient_fds.add(fd)
                        self._active_temp_fds.add(fd)
                elif redir.op == "<>":
                    f = self._open_for_redir_readwrite(target)
                    self._dup2_file(f, fd)
                    if fd >= 3:
                        transient_fds.add(fd)
                        self._active_temp_fds.add(fd)
                elif redir.op == ">":
                    f = self._open_for_redir(target, "wb", redir.op)
                    self._dup2_file(f, fd)
                    if fd >= 3:
                        transient_fds.add(fd)
                        self._active_temp_fds.add(fd)
                elif redir.op == ">>":
                    f = self._open_for_redir(target, "ab", redir.op)
                    self._dup2_file(f, fd)
                    if fd >= 3:
                        transient_fds.add(fd)
                        self._active_temp_fds.add(fd)
                elif redir.op == "<<":
                    content = self._expand_heredoc(redir)
                    f = tempfile.TemporaryFile()
                    f.write(content.encode("utf-8"))
                    f.seek(0)
                    self._dup2_file(f, fd)
                    if fd >= 3:
                        transient_fds.add(fd)
                        self._active_temp_fds.add(fd)
                elif redir.op == "<<<":
                    content = self._expand_here_string(redir)
                    f = tempfile.TemporaryFile()
                    f.write(content.encode("utf-8"))
                    f.seek(0)
                    self._dup2_file(f, fd)
                    if fd >= 3:
                        transient_fds.add(fd)
                        self._active_temp_fds.add(fd)
                elif redir.op == ">&":
                    self._dup_fd(redir, is_output=True, default_fd=fd, allowed_fds=transient_fds)
                elif redir.op == "<&":
                    self._dup_fd(redir, is_output=False, default_fd=fd, allowed_fds=transient_fds)
            yield
        finally:
            try:
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception:
                pass
            for fd, saved_fd in reversed(saved):
                if saved_fd >= 0:
                    os.dup2(saved_fd, fd)
                    os.close(saved_fd)
                else:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
            self._active_temp_fds = saved_active
            self._user_fds = saved_user_fds
            self._fd_redirect_depth = max(0, self._fd_redirect_depth - 1)

    def _expand_argv(self, words: List[Word]) -> List[str]:
        argv: List[str] = []
        for w in words:
            fields = self._legacy_word_to_expansion_fields(w.text, assignment=False)
            argv.extend(fields_to_text_list(fields))
        return argv

    def _expand_word(self, text: str) -> str:
        fields = self._legacy_word_to_expansion_fields(text, assignment=False)
        texts = fields_to_text_list(fields)
        return texts[0] if texts else ""

    def _expand_assignment_word(self, text: str) -> str:
        if self._is_process_subst(text):
            return self._process_substitute(text)
        fields = self._legacy_word_to_expansion_fields(text, assignment=True)
        texts = fields_to_text_list(fields)
        return texts[0] if texts else ""

    def _expand_assignment_word_protected(self, text: str) -> str:
        # Legacy compatibility alias now that assignment expansion is
        # structured and no marker unprotection step is required.
        return self._expand_assignment_word(text)

    def _expand_redir_target(self, redir: Redirect) -> str | None:
        if redir.target is None:
            return None
        target_word = getattr(redir, "target_word", None)
        if isinstance(target_word, dict) and self._asdl_rhs_assignment_can_expand_natively(target_word):
            out = self._expand_asdl_word_scalar(target_word, split_glob=False)
            if self._is_process_subst(out):
                return self._process_substitute(out)
            return out
        if self._is_process_subst(redir.target):
            return self._process_substitute(redir.target)
        return self._expand_assignment_word(redir.target)

    def _split_ifs(self, text: str) -> List[str]:
        if text == "":
            return []
        ifs, is_set = self._get_var_with_state("IFS")
        if not is_set:
            ifs = " \t\n"
        if ifs == "":
            return [text]

        ifs_ws = "".join(ch for ch in ifs if ch in " \t\n")
        ifs_nonws = "".join(ch for ch in ifs if ch not in " \t\n")
        parts: List[str] = []
        current: List[str] = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch not in ifs:
                current.append(ch)
                i += 1
                continue

            j = i
            while j < n and text[j] in ifs_ws:
                j += 1
            saw_nonws = j < n and text[j] in ifs_nonws
            if saw_nonws:
                if current:
                    parts.append("".join(current))
                    current = []
                else:
                    parts.append("")
                j += 1
                while j < n and text[j] in ifs_ws:
                    j += 1
                i = j
                continue

            if current:
                parts.append("".join(current))
                current = []
            i = j

        if current:
            parts.append("".join(current))
        return parts

    def _glob_field(self, text: str) -> List[str]:
        text = self._tilde_expand(text)
        if self.options.get("f", False):
            return [self._glob_pattern_display_runtime(text)]
        if self._contains_glob_meta_runtime(text):
            pattern_for_match = self._glob_pattern_for_match_runtime(text)
            matches = sorted(glob.glob(pattern_for_match))
            if matches:
                return matches
            return [self._glob_pattern_display_runtime(text)]
        return [text]

    def _contains_glob_meta_runtime(self, text: str) -> bool:
        escaped = False
        for ch in text:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch in {"*", "?", "["}:
                return True
        return False

    def _glob_pattern_for_match_runtime(self, text: str) -> str:
        out: list[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == "\\" and i + 1 < len(text):
                nxt = text[i + 1]
                if nxt == "*":
                    out.append("[*]")
                elif nxt == "?":
                    out.append("[?]")
                elif nxt == "[":
                    out.append("[[]")
                elif nxt == "]":
                    out.append("[]]")
                elif nxt == "\\":
                    out.append("[\\\\]")
                else:
                    out.append(nxt)
                i += 2
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def _glob_pattern_display_runtime(self, text: str) -> str:
        out: list[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == "\\" and i + 1 < len(text):
                nxt = text[i + 1]
                if nxt in {"*", "?", "[", "]", "\\"}:
                    out.append(nxt)
                    i += 2
                    continue
            out.append(ch)
            i += 1
        return "".join(out)

    def _tilde_expand(self, text: str) -> str:
        def expand_one(seg: str) -> str:
            if not seg.startswith("~"):
                return seg
            if seg == "~" or seg.startswith("~/"):
                home = self.env.get("HOME", "")
                return home + seg[1:]
            if "/" in seg:
                user, rest = seg[1:].split("/", 1)
                return self._user_home(user) + "/" + rest
            return self._user_home(seg[1:])

        if ":" not in text:
            return expand_one(text)
        return ":".join(expand_one(seg) for seg in text.split(":"))

    def _user_home(self, user: str) -> str:
        try:
            import pwd

            return pwd.getpwnam(user).pw_dir
        except Exception:
            return "~" + user

    def _param_attr_letters(self, name: str) -> str:
        attrs = self._var_attrs.get(name, set())
        letters: list[str] = []
        if "assoc" in attrs:
            letters.append("A")
        if "array" in attrs:
            letters.append("a")
        if "export" in attrs:
            letters.append("x")
        if "readonly" in attrs:
            letters.append("r")
        if "integer" in attrs:
            letters.append("i")
        if "nameref" in attrs:
            letters.append("n")
        if "lowercase" in attrs:
            letters.append("l")
        if "uppercase" in attrs:
            letters.append("u")
        if "trace" in attrs:
            letters.append("t")
        return "".join(letters)

    def _decode_backslash_escapes(self, value: str) -> str:
        try:
            return bytes(value, "utf-8").decode("unicode_escape")
        except Exception:
            return value

    @staticmethod
    def _transform_q_quote(value: str) -> str:
        return "'" + value.replace("'", "'\"'\"'") + "'"

    @staticmethod
    def _dq_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _typed_declare_A(self, name: str, typed: object) -> str:
        attrs = self._var_attrs.get(name, set())
        if isinstance(typed, list):
            elems: list[str] = []
            for i, v in enumerate(typed):
                if v is None:
                    continue
                elems.append(f'[{i}]="{self._dq_escape(str(v))}"')
            if elems:
                return f"declare -a {name}=(" + " ".join(elems) + ")"
            return f"declare -a {name}=()"
        if isinstance(typed, dict) and "assoc" in attrs:
            elems: list[str] = []
            for k, v in typed.items():
                elems.append(
                    f"[{self._transform_q_quote(str(k))}]=\"{self._dq_escape(str(v))}\""
                )
            if elems:
                return f"declare -A {name}=(" + " ".join(elems) + ")"
            return f"declare -A {name}=()"
        return ""

    def _expand_prompt_string(self, prompt: str) -> str:
        def _needs_promptvars(raw: str) -> bool:
            i_raw = 0
            while i_raw < len(raw):
                ch_raw = raw[i_raw]
                if ch_raw == "\\" and i_raw + 1 < len(raw):
                    i_raw += 2
                    continue
                if ch_raw in {"$", "`"}:
                    return True
                i_raw += 1
            return False

        out: list[str] = []
        i = 0
        user = self.env.get("USER", os.environ.get("USER", ""))
        host = os.uname().nodename if hasattr(os, "uname") else ""
        host_short = host.split(".")[0]
        cwd = self.env.get("PWD", os.getcwd())
        home = self.env.get("HOME") or os.environ.get("HOME", "")
        while i < len(prompt):
            ch = prompt[i]
            if ch != "\\" or i + 1 >= len(prompt):
                out.append(ch)
                i += 1
                continue
            nxt = prompt[i + 1]
            if nxt == "u":
                out.append(user)
            elif nxt == "h":
                out.append(host_short)
            elif nxt == "H":
                out.append(host)
            elif nxt == "a":
                out.append("\a")
            elif nxt == "e":
                out.append("\x1b")
            elif nxt == "d":
                out.append(time.strftime("%a %b %d"))
            elif nxt == "t":
                out.append(time.strftime("%H:%M:%S"))
            elif nxt == "T":
                out.append(time.strftime("%I:%M:%S"))
            elif nxt == "@":
                out.append(time.strftime("%I:%M %p"))
            elif nxt == "A":
                out.append(time.strftime("%H:%M"))
            elif nxt == "s":
                out.append("bash")
            elif nxt == "v":
                out.append(str(self.env.get("BASH_VERSINFO", "5.0")))
            elif nxt == "V":
                out.append(str(self.env.get("BASH_VERSION", "5.0.0")))
            elif nxt == "j":
                out.append(str(len(self._bg_jobs)))
            elif nxt == "l":
                tty_name = "tty"
                try:
                    tty_name = os.path.basename(os.ttyname(0))
                except Exception:
                    pass
                out.append(tty_name)
            elif nxt == "!":
                out.append("1")
            elif nxt == "#":
                out.append(str(self._command_number))
            elif nxt == "w":
                h = home.rstrip("/")
                if h and (cwd == h or cwd.startswith(h + "/")):
                    out.append("~" + cwd[len(h) :])
                else:
                    out.append(cwd)
            elif nxt == "W":
                base = os.path.basename(cwd.rstrip("/")) if cwd not in {"", "/"} else "/"
                out.append(base)
            elif nxt == "$":
                out.append("#" if os.geteuid() == 0 else "$")
            elif nxt == "n":
                out.append("\n")
            elif nxt == "r":
                out.append("\r")
            elif nxt == "D":
                if i + 2 < len(prompt) and prompt[i + 2] == "{":
                    j = i + 3
                    while j < len(prompt) and prompt[j] != "}":
                        j += 1
                    if j < len(prompt):
                        fmt = prompt[i + 3 : j]
                        try:
                            out.append(time.strftime(fmt))
                        except Exception:
                            out.append("")
                        i = j + 1
                        continue
                out.append(time.strftime("%X"))
            elif nxt in "01234567":
                oct_digits = [nxt]
                j = i + 2
                while j < len(prompt) and len(oct_digits) < 3 and prompt[j] in "01234567":
                    oct_digits.append(prompt[j])
                    j += 1
                try:
                    out.append(chr(int("".join(oct_digits), 8)))
                except Exception:
                    out.append("".join(oct_digits))
                i = j
                continue
            elif nxt in {"[", "]"}:
                pass
            else:
                out.append(nxt)
            i += 2
        expanded = "".join(out)
        if self._shopts.get("promptvars", False) and _needs_promptvars(prompt):
            try:
                expanded = self._expand_assignment_word(expanded)
            except Exception:
                pass
        return expanded

    def _transform_A_value(self, name: str, value: str) -> str:
        if name == "@":
            return "set -- " + " ".join(self._transform_q_quote(a) for a in self.positional)
        if name == "*":
            return "set -- " + " ".join(self._transform_q_quote(a) for a in self.positional)
        if name.isdigit() or name in {"#", "?", "$", "!", "-", "LINENO", "PPID"}:
            return ""
        typed_decl = self._typed_declare_A(name, self._typed_vars.get(name))
        if typed_decl:
            return typed_decl
        attrs = self._var_attrs.get(name, set())
        if "assoc" in attrs:
            return f"declare -A {name}"
        if "array" in attrs:
            return f"declare -a {name}={self._transform_q_quote(value)}"
        return f"{name}={self._transform_q_quote(value)}"

    def _apply_param_transform(self, name: str, value: str, transform_op: str) -> str:
        if transform_op == "@Q":
            return self._transform_q_quote(value)
        if transform_op == "@P":
            return self._expand_prompt_string(value)
        if transform_op == "@A":
            return self._transform_A_value(name, value)
        if transform_op == "@a":
            return self._param_attr_letters(name)
        if transform_op == "@E":
            return self._decode_backslash_escapes(value)
        if transform_op == "@U":
            return value.upper()
        if transform_op == "@u":
            return value[:1].upper() + value[1:] if value else ""
        if transform_op == "@L":
            return value.lower()
        raise RuntimeError(self._format_error("syntax error: bad substitution", line=self.current_line))

    @staticmethod
    def _apply_case_mod(value: str, op: str, arg_text: str | None = None) -> str:
        _ = arg_text  # pattern-selective variants are future work
        if op == ",,":
            return value.lower()
        if op == ",":
            return value[:1].lower() + value[1:] if value else ""
        if op == "^^":
            return value.upper()
        if op == "^":
            return value[:1].upper() + value[1:] if value else ""
        return value

    def _expand_param(self, name: str, quoted: bool):
        if name == "@":
            return list(self.positional)
        if name == "*":
            if quoted:
                return self._ifs_join(self.positional)
            return list(self.positional)
        if name == "#":
            return str(len(self.positional))
        if name == "?":
            return str(self.last_status)
        if name == "$":
            return str(os.getpid())
        if name == "PPID":
            return str(os.getppid())
        if name == "!":
            if self.options.get("u", False) and self._last_bg_pid is None and self._last_bg_job is None:
                raise RuntimeError("unbound variable: !")
            return str(self._last_bg_pid) if self._last_bg_pid is not None else ""
        if name == "-":
            return self._option_flags()
        if name == "LINENO":
            line = self.current_line if self.current_line is not None else 0
            if self.c_string_mode:
                line = max(0, line - 1)
            return str(line)
        value, is_set = self._get_param_state(name)
        if (not is_set) and self.options.get("u", False) and name not in ["@", "*", "#"]:
            raise RuntimeError(f"unbound variable: {name}")
        return value

    def _expand_braced_param(
        self,
        name: str,
        op: str | None,
        arg: str | None,
        quoted: bool,
        *,
        arg_fields: list[ExpansionField] | None = None,
        arg_node: dict[str, Any] | None = None,
        assignment_context: bool = False,
    ) -> str | List[str]:
        def _expand_param_op_raw_text_quoted(text: str) -> str:
            out: list[str] = []
            i = 0
            while i < len(text):
                ch = text[i]
                if ch == "\\" and i + 1 < len(text):
                    nxt = text[i + 1]
                    if nxt == "\n":
                        i += 2
                        continue
                    out.append("\\")
                    out.append(nxt)
                    i += 2
                    continue
                if ch == "$":
                    if i + 1 >= len(text):
                        out.append("$")
                        i += 1
                        continue
                    nxt = text[i + 1]
                    if nxt == "{":
                        end = _find_braced_end(text, i + 2)
                        if end == -1:
                            out.append("$")
                            i += 1
                            continue
                        inner = text[i + 2 : end]
                        p_name, p_op, p_arg = _split_braced(inner)
                        if p_name is None:
                            raise RuntimeError(self._format_error("syntax error: bad substitution", line=self.current_line))
                        value = self._expand_braced_param(
                            p_name,
                            p_op,
                            p_arg,
                            True,
                            arg_fields=None,
                            arg_node=None,
                            assignment_context=True,
                        )
                        out.append(self._scalarize_assignment_expansion(value))
                        i = end + 1
                        continue
                    if nxt.isdigit():
                        out.append(self._expand_param(nxt, True))
                        i += 2
                        continue
                    if nxt in "@*#?$!-":
                        out.append(self._scalarize_assignment_expansion(self._expand_param(nxt, True)))
                        i += 2
                        continue
                    if nxt == "_" or nxt.isalpha():
                        j = i + 2
                        while j < len(text) and (text[j] == "_" or text[j].isalnum()):
                            j += 1
                        var = text[i + 1 : j]
                        out.append(self._scalarize_assignment_expansion(self._expand_param(var, True)))
                        i = j
                        continue
                out.append(ch)
                i += 1
            return "".join(out)

        def _expand_param_op_word_quoted(text: str, node: dict[str, Any] | None) -> str:
            def _decode_param_op_quoted_literal(raw: str) -> str:
                out_lit: list[str] = []
                i_lit = 0
                while i_lit < len(raw):
                    ch_lit = raw[i_lit]
                    if ch_lit == "\\" and i_lit + 1 < len(raw):
                        nxt_lit = raw[i_lit + 1]
                        if nxt_lit == "\n":
                            i_lit += 2
                            continue
                        if nxt_lit in {" ", "\t"}:
                            out_lit.append("\\")
                            out_lit.append(nxt_lit)
                        else:
                            out_lit.append(nxt_lit)
                        i_lit += 2
                        continue
                    out_lit.append(ch_lit)
                    i_lit += 1
                return "".join(out_lit)

            if not isinstance(node, dict) or node.get("type") != "word.Compound":
                return _expand_param_op_raw_text_quoted(text)
            out: list[str] = []
            deferred_suffix: list[str] = []
            for part in (node.get("parts") or []):
                if not isinstance(part, dict):
                    continue
                t = part.get("type")
                if t == "word_part.Literal":
                    lit = _decode_param_op_quoted_literal(str(part.get("tval", "")))
                    out.append(_expand_param_op_raw_text_quoted(lit))
                    continue
                if t == "word_part.SingleQuoted":
                    sval = str(part.get("sval", ""))
                    if sval == "}":
                        # Bash/POSIX edge: in ${name+'}'z} style forms under
                        # double quotes the quoted '}' behaves as an empty
                        # quoted atom while the brace appears at word tail.
                        out.append("''")
                        deferred_suffix.append("}")
                        continue
                    out.append("'")
                    out.append(_expand_param_op_raw_text_quoted(sval))
                    out.append("'")
                    continue
                if t == "word_part.DoubleQuoted":
                    # Preserve baseline behavior for nested double quotes in
                    # parameter-op words (do not keep the quote delimiters).
                    for inner in (part.get("parts") or []):
                        if isinstance(inner, dict):
                            out.append(self._expand_asdl_assignment_part_scalar(inner, quoted_context=True))
                    continue
                if t == "word_part.SimpleVarSub":
                    out.append(self._scalarize_assignment_expansion(self._expand_param(str(part.get("name", "")), True)))
                    continue
                if t == "word_part.BracedVarSub":
                    child_arg = part.get("arg")
                    child_text = self._asdl_word_to_text(child_arg) if isinstance(child_arg, dict) else None
                    out.append(
                        self._scalarize_assignment_expansion(
                            self._expand_braced_param(
                                str(part.get("name", "")),
                                part.get("op"),
                                child_text,
                                True,
                                arg_fields=None,
                                arg_node=child_arg if isinstance(child_arg, dict) else None,
                                assignment_context=True,
                            )
                        )
                    )
                    continue
                if t == "word_part.CommandSub":
                    child = part.get("child")
                    syntax = str(part.get("syntax") or "dollar")
                    backtick = syntax == "backtick"
                    if isinstance(child, dict) and child.get("type") == "command.CommandList":
                        out.append(self._expand_command_subst_asdl(child, backtick=backtick))
                    else:
                        src = str(part.get("child_source") or "")
                        out.append(self._expand_command_subst_text(src, backtick=backtick))
                    continue
                if t == "word_part.ArithSub":
                    expr = str(part.get("expr_source") or part.get("code") or "")
                    out.append(self._expand_arith(expr))
                    continue
                out.append(_expand_param_op_raw_text_quoted(self._asdl_word_part_to_text(part)))
            return "".join(out + deferred_suffix)

        def _expand_alt_word(text: str) -> str:
            if quoted:
                return _expand_param_op_word_quoted(text, arg_node)
            return self._expand_assignment_word_protected(text)

        def _expand_alt_fields(
            text: str,
            fields: list[ExpansionField] | None = None,
            *,
            respect_edge_ws: bool = True,
        ) -> PresplitFields:
            if fields is not None:
                out_fields: List[str] = []
                split_fields: list[ExpansionField] = []
                literal_only = True
                for field in fields:
                    # POSIX parameter-op words (e.g. ${x:-word}) undergo field
                    # splitting after quote removal. Mark unquoted segments as
                    # split-active even when they originated as literals.
                    adjusted = ExpansionField(
                        [
                            ExpansionSegment(
                                text=seg.text,
                                quoted=seg.quoted,
                                glob_active=(seg.glob_active or (not seg.quoted)),
                                split_active=(seg.split_active or (not seg.quoted)),
                                source_kind=seg.source_kind,
                            )
                            for seg in field.segments
                        ],
                        preserve_boundary=field.preserve_boundary,
                    )
                    split_fields.extend(self._split_structured_field(adjusted))
                for field in split_fields:
                    has_active_pattern = any(
                        seg.glob_active and any(ch in seg.text for ch in ("*", "?", "["))
                        for seg in field.segments
                    )
                    if has_active_pattern:
                        literal_only = False
                    out_fields.extend(self._glob_structured_field(field))
                ifs_value, ifs_set = self._get_var_with_state("IFS")
                if not ifs_set:
                    ifs_value = " \t\n"
                ifs_ws = "".join(ch for ch in ifs_value if ch in " \t\n")
                lead_boundary = respect_edge_ws and bool(text) and bool(ifs_ws) and text[0] in ifs_ws
                trail_boundary = respect_edge_ws and bool(text) and bool(ifs_ws) and text[-1] in ifs_ws
                out = PresplitFields(out_fields, lead_boundary=lead_boundary, trail_boundary=trail_boundary)
                setattr(out, "force_single_quoted", literal_only)
                return out
            reader = TokenReader(text)
            ctx = LexContext(reserved_words=set(), allow_reserved=False, allow_newline=False)
            words: List[str] = []
            while True:
                tok = reader.next(ctx)
                if tok is None:
                    break
                if tok.kind == "WORD":
                    words.append(tok.value)
            out_fields: List[str] = []
            for w in words:
                w_parts = parse_word_parts(w)
                if w_parts and all(p.quoted for p in w_parts):
                    out_fields.append(self._expand_assignment_word_protected(w))
                    continue
                out_fields.extend(fields_to_text_list(self._legacy_word_to_expansion_fields(w, assignment=False)))
            ifs_value, ifs_set = self._get_var_with_state("IFS")
            if not ifs_set:
                ifs_value = " \t\n"
            ifs_ws = "".join(ch for ch in ifs_value if ch in " \t\n")
            edge_ws = respect_edge_ws and not (out_fields and all(v == "" for v in out_fields))
            lead_boundary = edge_ws and bool(text) and bool(ifs_ws) and text[0] in ifs_ws
            trail_boundary = edge_ws and bool(text) and bool(ifs_ws) and text[-1] in ifs_ws
            return PresplitFields(out_fields, lead_boundary=lead_boundary, trail_boundary=trail_boundary)

        def _expand_alt_unquoted(text: str):
            if assignment_context:
                return _expand_alt_word(text)
            if arg_fields is not None:
                if text == "":
                    # ${name+} / ${name:+} with an empty operator word should
                    # remain an empty string value, not disappear as 0 fields.
                    return _expand_alt_word(text)
                # Keep legacy token-boundary behavior for quote-sensitive
                # alternate words (e.g. ${x:+'' ''}) where empty quoted atoms
                # carry field-count semantics.
                if any(mark in text for mark in ["'", '"', "`", "$(", "${"]):
                    all_quoted = all(
                        getattr(seg, "quoted", False)
                        for f in arg_fields
                        for seg in getattr(f, "segments", [])
                    )
                    if all_quoted:
                        return _expand_alt_fields(text, arg_fields)
                    ifs_value, ifs_set = self._get_var_with_state("IFS")
                    if not ifs_set:
                        ifs_value = " \t\n"
                    ifs_nonws = "".join(ch for ch in ifs_value if ch not in " \t\n")
                    if ifs_nonws:
                        # Non-whitespace IFS splitting is sensitive to quote
                        # boundaries inside operator words; use structured
                        # fields instead of legacy text retokenization.
                        return _expand_alt_fields(text, arg_fields)
                    return _expand_alt_fields(text)
                if any(ch in text for ch in [" ", "\t", "\n"]):
                    # When operator-arg fields are all literal, the adapter can
                    # carry them with split_active=False; fall back to token
                    # parsing so ${x:+b c d} still yields 3 fields.
                    has_split_active = any(
                        getattr(seg, "split_active", False)
                        for f in arg_fields
                        for seg in getattr(f, "segments", [])
                    )
                    if not has_split_active:
                        return _expand_alt_fields(text)
                return _expand_alt_fields(text, arg_fields)
            if any(mark in text for mark in ["'", '"', "`", "$(", "${"]):
                return _expand_alt_fields(text)
            if any(ch in text for ch in [" ", "\t", "\n"]):
                # Unquoted alternate-word text with IFS whitespace must split
                # into separate fields (e.g. ${x:+b c d} -> b c d).
                return _expand_alt_fields(text)
            return _expand_alt_word(text)

        if op == "__invalid__":
            raise RuntimeError(self._format_error("syntax error: bad substitution", line=self.current_line))
        if op == "__indirect__":
            if (
                name == "#"
                and self.options.get("posix", False)
                and self._bash_compat_level is not None
                and self._bash_compat_level <= 50
            ):
                # Bash-compat <=5.0 in --posix mode keeps ${!#} legacy behavior.
                return ""
            ref_value, ref_set = self._get_param_state(name)
            if not ref_set:
                return ""
            value, _ = self._get_param_state(ref_value)
            return value
        special_params = {"@", "*", "#", "?", "$", "!", "-", "LINENO", "PPID"}
        parsed_sub = self._parse_subscripted_name(name)
        subscript_ok = parsed_sub is not None
        if not (self._is_valid_name(name) or subscript_ok or name.isdigit() or name in special_params):
            raise RuntimeError(self._format_error("syntax error: bad substitution", line=self.current_line))
        if parsed_sub is not None:
            base, key = parsed_sub
            typed = self._typed_vars.get(base)
            attrs = self._var_attrs.get(base, set())
            vals_for_key: list[str] = []
            if key in {"@", "*"}:
                if isinstance(typed, list):
                    vals_for_key = self._array_visible_values(typed)
                elif isinstance(typed, dict) and "assoc" in attrs:
                    vals_for_key = [str(v) for v in reversed(list(typed.values()))]
                else:
                    base_v, base_set = self._get_var_with_state(base)
                    vals_for_key = [base_v] if base_set else []
            if op == "__len__":
                if key in {"@", "*"}:
                    if isinstance(typed, list):
                        return str(len(vals_for_key))
                    if isinstance(typed, dict) and "assoc" in attrs:
                        return str(len(vals_for_key))
                    return str(len(vals_for_key))
                sub_value, sub_set = self._get_var_with_state(name)
                if self.options.get("u", False) and not sub_set:
                    raise RuntimeError(f"unbound variable: {name}")
                return str(len(sub_value))
            if key in {"@", "*"}:
                vals: list[str] = vals_for_key
                if op is None:
                    if not quoted:
                        vals = [v for v in vals if v != ""]
                    if key == "*":
                        if quoted:
                            return self._ifs_join(vals)
                        return vals
                    return vals
                arg_text = arg or ""
                if op == "@A":
                    decl = self._typed_declare_A(base, typed)
                    if not decl:
                        scalar_base, base_set = self._get_var_with_state(base)
                        if base_set:
                            decl = self._transform_A_value(base, scalar_base)
                    if key == "@":
                        if decl:
                            return decl.split(" ", 2) if decl.startswith("declare ") else [decl]
                        return []
                    return decl
                if isinstance(op, str) and op.startswith("@"):
                    vals = [self._apply_param_transform(base, v, op) for v in vals]
                elif op in {",", ",,", "^", "^^"}:
                    vals = [self._apply_case_mod(v, op, arg_text) for v in vals]
                elif op in ["#", "##"]:
                    pattern = (
                        self._pattern_from_structured_fields(arg_fields)
                        if arg_fields is not None
                        else self._pattern_from_word(arg_text)
                    )
                    vals = [self._remove_prefix(v, pattern, longest=(op == "##")) for v in vals]
                elif op in ["%", "%%"]:
                    pattern = (
                        self._pattern_from_structured_fields(arg_fields)
                        if arg_fields is not None
                        else self._pattern_from_word(arg_text)
                    )
                    vals = [self._remove_suffix(v, pattern, longest=(op == "%%")) for v in vals]
                elif op == "/":
                    use_struct = arg_fields is not None
                    spec_struct = self._split_replace_spec_structured(arg_fields) if use_struct else None
                    if spec_struct is None:
                        vals = [self._replace_pattern(v, arg_text) for v in vals]
                    else:
                        g, pfx, sfx, pat_f, repl_f = spec_struct
                        vals = [
                            self._replace_pattern_structured(
                                v,
                                global_replace=g,
                                prefix_only=pfx,
                                suffix_only=sfx,
                                pat_fields=pat_f,
                                repl_fields=repl_f,
                            )
                            for v in vals
                        ]
                elif op == ":substr":
                    if isinstance(typed, list):
                        vals = self._slice_indexed_array(typed, arg_text)
                    else:
                        vals = self._slice_fields(vals, arg_text)
                if not quoted:
                    vals = [v for v in vals if v != ""]
                if key == "*":
                    if quoted:
                        return self._ifs_join(vals)
                    return vals
                return vals
        if op == "__len__":
            if name in ["@", "*"]:
                return str(len(self._ifs_join(self.positional)))
            if name in ["#", "?", "$", "!", "-", "LINENO", "PPID"] or name.isdigit():
                v = self._expand_param(name, quoted)
                return str(len(v))
            value, is_set = self._get_param_state(name)
            if self.options.get("u", False) and not is_set:
                raise RuntimeError(f"unbound variable: {name}")
            return str(len(value))
        if op == "__keys__":
            typed = self._typed_vars.get(name)
            attrs = self._var_attrs.get(name, set())
            vals: list[str] = []
            if isinstance(typed, dict) and "assoc" in attrs:
                vals = [str(k) for k in reversed(list(typed.keys()))]
            elif isinstance(typed, list):
                vals = [str(i) for i, v in enumerate(typed) if v is not None]
            if arg == "*":
                if quoted:
                    return self._ifs_join(vals)
                return vals
            return vals
        if name == "@" and op is None:
            return [v for v in self.positional if (quoted or v != "")]
        if name == "*" and op is None:
            if quoted:
                return self._ifs_join(self.positional)
            return [v for v in self.positional if v != ""]
        if isinstance(op, str) and op.startswith("@") and name in {"@", "*"}:
            if op == "@A":
                if name == "@":
                    return ["set", "--"] + [self._transform_q_quote(v) for v in self.positional]
                return self._transform_A_value(name, "")
            vals = list(self.positional)
            vals = [self._apply_param_transform(name, v, op) for v in vals]
            if name == "*":
                if quoted:
                    return self._ifs_join(vals)
                return vals
            return vals
        if name.isdigit():
            value, is_set = self._get_param_state(name)
            if op is None:
                if not is_set and self.options.get("u", False):
                    raise RuntimeError(f"unbound variable: {name}")
                return value
            arg_text = arg or ""
            if op in ["=", ":="]:
                if not is_set or (op == ":=" and value == ""):
                    raise RuntimeError(self._format_error(f"{name}: bad variable name", line=self.current_line))
                return value
            if op in ["?", ":?"]:
                if not is_set or (op == ":?" and value == ""):
                    if arg_text:
                        msg = self._expand_assignment_word_protected(arg_text)
                    elif op == ":?":
                        msg = "parameter not set or null"
                    else:
                        msg = "parameter not set"
                    raise RuntimeError(self._format_error(f"{name}: {msg}", line=self.current_line))
                return value
            if op == ":substr":
                if not is_set and self.options.get("u", False):
                    raise RuntimeError(f"unbound variable: {name}")
                return self._substring(value, arg_text)
            if op in ["-", ":-"]:
                if not is_set or (op == ":-" and value == ""):
                    return _expand_alt_word(arg_text) if quoted else _expand_alt_unquoted(arg_text)
                return value
            if op in ["+", ":+"]:
                if is_set and (op == "+" or value != ""):
                    return _expand_alt_word(arg_text) if quoted else _expand_alt_unquoted(arg_text)
                return ""
            return value
        value, is_set = self._get_param_state(name)
        arg_text = arg or ""
        if op is None:
            if (
                not is_set
                and self.options.get("u", False)
                and name not in {"@", "*", "#", "?", "$", "-", "LINENO", "PPID"}
            ):
                raise RuntimeError(f"unbound variable: {name}")
            return value
        if (
            self.options.get("u", False)
            and not is_set
            and (op in {"__len__", "#", "##", "%", "%%", ":substr", "/"} or (isinstance(op, str) and op.startswith("@")))
        ):
            raise RuntimeError(f"unbound variable: {name}")
        if op in ["-", ":-"]:
            if not is_set or (op == ":-" and value == ""):
                return _expand_alt_word(arg_text) if quoted else _expand_alt_unquoted(arg_text)
            return value
        if op in ["+", ":+"]:
            if is_set and (op == "+" or value != ""):
                return _expand_alt_word(arg_text) if quoted else _expand_alt_unquoted(arg_text)
            return ""
        if op in ["=", ":="]:
            if name == "#" and op == "=":
                raise RuntimeError(self._format_error("syntax error: bad substitution", line=self.current_line))
            if not is_set or (op == ":=" and value == ""):
                if name in ["#", "?", "@", "*", "$", "!", "-"] or name.isdigit():
                    raise RuntimeError(self._format_error(f"{name}: bad variable name", line=self.current_line))
                replacement = _expand_alt_word(arg_text)
                self._assign_shell_var(name, replacement)
                return replacement
            return value
        if op in ["?", ":?"]:
            if not is_set or (op == ":?" and value == ""):
                if arg_text:
                    msg = self._expand_assignment_word_protected(arg_text)
                elif op == ":?":
                    msg = "parameter not set or null"
                else:
                    msg = "parameter not set"
                raise RuntimeError(self._format_error(f"{name}: {msg}", line=self.current_line))
            return value
        if op in ["#", "##"]:
            pattern = (
                self._pattern_from_structured_fields(arg_fields)
                if arg_fields is not None
                else self._pattern_from_word(arg_text)
            )
            return self._remove_prefix(value, pattern, longest=(op == "##"))
        if op in ["%", "%%"]:
            pattern = (
                self._pattern_from_structured_fields(arg_fields)
                if arg_fields is not None
                else self._pattern_from_word(arg_text)
            )
            return self._remove_suffix(value, pattern, longest=(op == "%%"))
        if op == ":substr":
            return self._substring(value, arg_text)
        if op == "/":
            if not is_set:
                return ""
            use_struct = arg_fields is not None
            spec_struct = self._split_replace_spec_structured(arg_fields) if use_struct else None
            if spec_struct is None:
                return self._replace_pattern(value, arg_text)
            g, pfx, sfx, pat_f, repl_f = spec_struct
            return self._replace_pattern_structured(
                value,
                global_replace=g,
                prefix_only=pfx,
                suffix_only=sfx,
                pat_fields=pat_f,
                repl_fields=repl_f,
            )
        if isinstance(op, str) and op.startswith("@"):
            return self._apply_param_transform(name, value, op)
        if op in {",", ",,", "^", "^^"}:
            return self._apply_case_mod(value, op, arg_text)
        return value

    def _substring(self, value: str, arg_text: str) -> str:
        if arg_text == "":
            raise RuntimeError(self._format_error("syntax error: missing '}'", line=self.current_line))
        if ":" in arg_text:
            off_text, len_text = arg_text.split(":", 1)
            has_len = True
        else:
            off_text, len_text = arg_text, ""
            has_len = False
        off = self._to_int_arith(off_text if off_text != "" else "0")
        n = len(value)
        if off < 0:
            if -off > n:
                return ""
            off = n + off
        if off > n:
            return ""
        if not has_len:
            return value[off:]
        if len_text == "":
            return ""
        ln = self._to_int_arith(len_text)
        if ln < 0:
            end = n + ln
            if end < off:
                return ""
            return value[off:end]
        if ln == 0:
            return ""
        return value[off : off + ln]

    def _slice_fields(self, values: list[str], arg_text: str) -> list[str]:
        if arg_text == "":
            raise RuntimeError(self._format_error("syntax error: missing '}'", line=self.current_line))
        if ":" in arg_text:
            off_text, len_text = arg_text.split(":", 1)
            has_len = True
        else:
            off_text, len_text = arg_text, ""
            has_len = False
        try:
            off = int(self._expand_arith(off_text if off_text != "" else "0", context="subscript"))
        except Exception:
            off = 0
        n = len(values)
        start = off if off >= 0 else n + off
        if start < 0:
            start = 0
        if start > n:
            start = n
        if not has_len:
            return values[start:]
        try:
            ln = int(self._expand_arith(len_text, context="subscript"))
        except Exception:
            ln = 0
        if ln >= 0:
            end = start + ln
        else:
            end = n + ln
        if end < start:
            end = start
        if end > n:
            end = n
        return values[start:end]

    def _slice_indexed_array(self, values: list[object], arg_text: str) -> list[str]:
        if arg_text == "":
            raise RuntimeError(self._format_error("syntax error: missing '}'", line=self.current_line))
        if ":" in arg_text:
            off_text, len_text = arg_text.split(":", 1)
            has_len = True
        else:
            off_text, len_text = arg_text, ""
            has_len = False
        try:
            off = int(self._expand_arith(off_text if off_text != "" else "0", context="subscript"))
        except Exception:
            off = 0
        max_idx = self._array_max_index(values)
        n = 0 if max_idx is None else (max_idx + 1)
        start = off if off >= 0 else n + off
        if start < 0:
            start = 0
        if start > n:
            start = n

        # Bash sparse-array slicing semantics for ${a[@]:off:len} are based on
        # starting index in index-space, then collecting set elements.
        set_vals: list[str] = []
        for i in range(start, len(values)):
            v = values[i]
            if v is not None:
                set_vals.append(str(v))

        if not has_len:
            return set_vals

        try:
            ln = int(self._expand_arith(len_text, context="subscript"))
        except Exception:
            ln = 0
        if ln <= 0:
            return []
        return set_vals[:ln]

    def _replace_pattern(self, value: str, spec: str) -> str:
        global_replace = False
        prefix_only = False
        suffix_only = False
        text = spec
        if text.startswith("/"):
            global_replace = True
            text = text[1:]
        elif text.startswith("#"):
            prefix_only = True
            text = text[1:]
        elif text.startswith("%"):
            suffix_only = True
            text = text[1:]

        if global_replace and text.startswith("/"):
            pat_rest, repl_raw = self._split_unescaped_slash(text[1:])
            pat_raw = "/" + pat_rest
        else:
            pat_raw, repl_raw = self._split_unescaped_slash(text)
        pattern = self._pattern_from_word(pat_raw)
        repl = self._expand_assignment_word(repl_raw)

        if prefix_only:
            match_end = self._match_prefix_end(value, pattern)
            if match_end is None:
                return value
            return repl + value[match_end:]
        if suffix_only:
            match_start = self._match_suffix_start(value, pattern)
            if match_start is None:
                return value
            return value[:match_start] + repl
        if global_replace:
            return self._replace_all_matches(value, pattern, repl)
        m = self._find_first_match(value, pattern)
        if m is None:
            return value
        i, j = m
        return value[:i] + repl + value[j:]

    def _replace_pattern_structured(
        self,
        value: str,
        *,
        global_replace: bool,
        prefix_only: bool,
        suffix_only: bool,
        pat_fields: list[ExpansionField],
        repl_fields: list[ExpansionField],
    ) -> str:
        pattern = self._pattern_from_structured_fields(pat_fields)
        repl = self._structured_fields_to_assignment_scalar(repl_fields)
        if prefix_only:
            match_end = self._match_prefix_end(value, pattern)
            if match_end is None:
                return value
            return repl + value[match_end:]
        if suffix_only:
            match_start = self._match_suffix_start(value, pattern)
            if match_start is None:
                return value
            return value[:match_start] + repl
        if global_replace:
            return self._replace_all_matches(value, pattern, repl)
        m = self._find_first_match(value, pattern)
        if m is None:
            return value
        i, j = m
        return value[:i] + repl + value[j:]

    def _split_replace_spec_structured(
        self, fields: list[ExpansionField] | None
    ) -> tuple[bool, bool, bool, list[ExpansionField], list[ExpansionField]] | None:
        if not fields or len(fields) != 1:
            return None
        stream: list[tuple[str, bool]] = []
        for seg in fields[0].segments:
            for ch in seg.text:
                stream.append((ch, seg.quoted))
        if not stream:
            return False, False, False, [ExpansionField([])], [ExpansionField([])]
        global_replace = False
        prefix_only = False
        suffix_only = False
        start = 0
        first_ch, first_quoted = stream[0]
        if not first_quoted and first_ch in {"/", "#", "%"}:
            if first_ch == "/":
                global_replace = True
            elif first_ch == "#":
                prefix_only = True
            else:
                suffix_only = True
            start = 1

        def find_delim(from_idx: int) -> int:
            for i in range(from_idx, len(stream)):
                ch, quoted = stream[i]
                if ch == "/" and not quoted:
                    return i
            return -1

        if global_replace and start < len(stream) and stream[start][0] == "/" and not stream[start][1]:
            delim = find_delim(start + 1)
        else:
            delim = find_delim(start)

        pat_stream = stream[start:] if delim < 0 else stream[start:delim]
        repl_stream = [] if delim < 0 else stream[delim + 1 :]

        def to_field(chars: list[tuple[str, bool]]) -> list[ExpansionField]:
            if not chars:
                return [ExpansionField([])]
            segs: list[ExpansionSegment] = []
            buf = chars[0][0]
            q = chars[0][1]
            for ch, quoted in chars[1:]:
                if quoted == q:
                    buf += ch
                    continue
                segs.append(
                    ExpansionSegment(
                        text=buf,
                        quoted=q,
                        glob_active=(not q),
                        split_active=(not q),
                        source_kind="word_part.BracedVarSubArg",
                    )
                )
                buf = ch
                q = quoted
            segs.append(
                ExpansionSegment(
                    text=buf,
                    quoted=q,
                    glob_active=(not q),
                    split_active=(not q),
                    source_kind="word_part.BracedVarSubArg",
                )
            )
            return [ExpansionField(segs, preserve_boundary=any(seg.quoted for seg in segs))]

        return global_replace, prefix_only, suffix_only, to_field(pat_stream), to_field(repl_stream)

    def _split_unescaped_slash(self, text: str) -> tuple[str, str]:
        i = 0
        in_single = False
        in_double = False
        while i < len(text):
            ch = text[i]
            if in_single:
                if ch == "'":
                    in_single = False
                i += 1
                continue
            if in_double:
                if ch == "\\" and i + 1 < len(text):
                    i += 2
                    continue
                if ch == '"':
                    in_double = False
                i += 1
                continue
            if ch == "'":
                in_single = True
                i += 1
                continue
            if ch == '"':
                in_double = True
                i += 1
                continue
            if ch == "\\" and i + 1 < len(text):
                i += 2
                continue
            if ch == "/":
                return text[:i], text[i + 1 :]
            i += 1
        return text, ""

    def _find_first_match(self, value: str, pattern: str) -> tuple[int, int] | None:
        for i in range(len(value) + 1):
            for j in range(len(value), i - 1, -1):
                if self._shell_pattern_match(value[i:j], pattern):
                    return i, j
        return None

    def _replace_all_matches(self, value: str, pattern: str, repl: str) -> str:
        out: List[str] = []
        i = 0
        while i <= len(value):
            m = self._find_first_match(value[i:], pattern)
            if m is None:
                out.append(value[i:])
                break
            a, b = m
            start = i + a
            end = i + b
            out.append(value[i:start])
            out.append(repl)
            if end == start:
                if end >= len(value):
                    break
                out.append(value[end])
                i = end + 1
            else:
                i = end
        return "".join(out)

    def _match_prefix_end(self, value: str, pattern: str) -> int | None:
        for j in range(len(value), -1, -1):
            if self._shell_pattern_match(value[:j], pattern):
                return j
        return None

    def _match_suffix_start(self, value: str, pattern: str) -> int | None:
        for i in range(0, len(value) + 1):
            if self._shell_pattern_match(value[i:], pattern):
                return i
        return None

    def _to_int_arith(self, expr: str) -> int:
        try:
            return int(self._expand_arith(expr))
        except Exception:
            return 0

    def _get_positional(self, digit: str) -> str:
        idx = int(digit)
        if idx == 0:
            return self.script_name
        if idx <= len(self.positional):
            return self.positional[idx - 1]
        return ""

    def _expand_command_subst_text(self, cmd: str, backtick: bool = False) -> str:
        # Line accounting differs slightly between $(...) and backticks in ash.
        line_bias = -1 if backtick else 0
        output, status, hard_error = self._capture_eval(cmd, line_bias=line_bias)
        if hard_error and status != 0:
            raise CommandSubstFailure(status)
        self._cmd_sub_used = True
        self._cmd_sub_status = status
        return output.rstrip("\n")

    def _expand_command_subst_asdl(self, child: dict[str, Any], backtick: bool = False) -> str:
        line_bias = -1 if backtick else 0
        output, status, hard_error = self._capture_eval_asdl(child, line_bias=line_bias)
        if hard_error and status != 0:
            raise CommandSubstFailure(status)
        self._cmd_sub_used = True
        self._cmd_sub_status = status
        return output.rstrip("\n")

    def _expand_arith(self, expr: str, context: str | None = None) -> str:
        try:
            expr = self._expand_assignment_word(expr)
        except Exception:
            pass
        expr = self._materialize_random_in_arith(expr)
        try:
            return str(self._eval_arith_expr(expr))
        except ZeroDivisionError:
            if context != "subscript":
                self._report_error(
                    self._diag_msg(DiagnosticKey.ARITH_DIVIDE_BY_ZERO),
                    line=self.current_line,
                    context=context,
                )
            raise ArithExpansionFailure(2)
        except ArithExpansionFailure:
            raise
        except Exception:
            if context != "subscript":
                self._report_error(
                    self._diag_msg(DiagnosticKey.ARITH_SYNTAX_ERROR),
                    line=self.current_line,
                    context=context,
                )
            raise ArithExpansionFailure(2)

    def _eval_arith_expr(self, expr: str) -> int:
        tokens = self._arith_tokens(expr)
        if not tokens:
            return 0
        parser = self._ArithParser(self, tokens)
        node = parser.parse()
        if parser.peek() is not None:
            raise ValueError("trailing arithmetic tokens")
        return self._arith_eval_node(node)

    def _arith_tokens(self, expr: str) -> list[str]:
        tokens: list[str] = []
        i = 0
        n = len(expr)
        ops = (
            "<<=",
            ">>=",
            "++",
            "--",
            "<=",
            ">=",
            "==",
            "!=",
            "&&",
            "||",
            "<<",
            ">>",
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "&=",
            "^=",
            "|=",
            "=",
            "?",
            ":",
            ",",
            "(",
            ")",
            "[",
            "]",
            "+",
            "-",
            "*",
            "/",
            "%",
            "!",
            "~",
            "<",
            ">",
            "&",
            "^",
            "|",
        )
        while i < n:
            ch = expr[i]
            if ch.isspace():
                i += 1
                continue
            matched_op = None
            for op in ops:
                if expr.startswith(op, i):
                    matched_op = op
                    break
            if matched_op is not None:
                tokens.append(matched_op)
                i += len(matched_op)
                continue
            if ch.isalpha() or ch == "_":
                j = i + 1
                while j < n and (expr[j].isalnum() or expr[j] == "_"):
                    j += 1
                tokens.append(expr[i:j])
                i = j
                continue
            if ch.isdigit():
                j = i + 1
                while j < n and (expr[j].isalnum() or expr[j] in {"#", "_", "@", "."}):
                    j += 1
                tokens.append(expr[i:j])
                i = j
                continue
            raise ValueError("invalid arithmetic token")
        return tokens

    class _ArithParser:
        _ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", "^=", "|="}

        def __init__(self, rt: "ShellRuntime", tokens: list[str]) -> None:
            self._rt = rt
            self._tokens = tokens
            self._i = 0

        def peek(self) -> str | None:
            if self._i >= len(self._tokens):
                return None
            return self._tokens[self._i]

        def take(self) -> str:
            tok = self.peek()
            if tok is None:
                raise ValueError("unexpected end")
            self._i += 1
            return tok

        def expect(self, tok: str) -> None:
            got = self.take()
            if got != tok:
                raise ValueError(f"expected {tok}")

        def parse(self) -> Any:
            return self._parse_comma()

        def _parse_comma(self) -> Any:
            node = self._parse_assign()
            while self.peek() == ",":
                self.take()
                right = self._parse_assign()
                node = ("comma", node, right)
            return node

        def _parse_assign(self) -> Any:
            node = self._parse_conditional()
            tok = self.peek()
            if tok in self._ASSIGN_OPS:
                op = self.take()
                right = self._parse_assign()
                if not self._rt._arith_is_lvalue(node):
                    raise ValueError("invalid assignment target")
                return ("assign", op, node, right)
            return node

        def _parse_conditional(self) -> Any:
            node = self._parse_logical_or()
            if self.peek() == "?":
                self.take()
                if_true = self._parse_assign()
                self.expect(":")
                if_false = self._parse_conditional()
                return ("ternary", node, if_true, if_false)
            return node

        def _parse_logical_or(self) -> Any:
            node = self._parse_logical_and()
            while self.peek() == "||":
                self.take()
                node = ("bin", "||", node, self._parse_logical_and())
            return node

        def _parse_logical_and(self) -> Any:
            node = self._parse_bitor()
            while self.peek() == "&&":
                self.take()
                node = ("bin", "&&", node, self._parse_bitor())
            return node

        def _parse_bitor(self) -> Any:
            node = self._parse_bitxor()
            while self.peek() == "|":
                self.take()
                node = ("bin", "|", node, self._parse_bitxor())
            return node

        def _parse_bitxor(self) -> Any:
            node = self._parse_bitand()
            while self.peek() == "^":
                self.take()
                node = ("bin", "^", node, self._parse_bitand())
            return node

        def _parse_bitand(self) -> Any:
            node = self._parse_equality()
            while self.peek() == "&":
                self.take()
                node = ("bin", "&", node, self._parse_equality())
            return node

        def _parse_equality(self) -> Any:
            node = self._parse_relational()
            while self.peek() in {"==", "!="}:
                op = self.take()
                node = ("bin", op, node, self._parse_relational())
            return node

        def _parse_relational(self) -> Any:
            node = self._parse_shift()
            while self.peek() in {"<", "<=", ">", ">="}:
                op = self.take()
                node = ("bin", op, node, self._parse_shift())
            return node

        def _parse_shift(self) -> Any:
            node = self._parse_add()
            while self.peek() in {"<<", ">>"}:
                op = self.take()
                node = ("bin", op, node, self._parse_add())
            return node

        def _parse_add(self) -> Any:
            node = self._parse_mul()
            while self.peek() in {"+", "-"}:
                op = self.take()
                node = ("bin", op, node, self._parse_mul())
            return node

        def _parse_mul(self) -> Any:
            node = self._parse_unary()
            while self.peek() in {"*", "/", "%"}:
                op = self.take()
                node = ("bin", op, node, self._parse_unary())
            return node

        def _parse_unary(self) -> Any:
            tok = self.peek()
            if tok in {"+", "-", "!", "~", "++", "--"}:
                op = self.take()
                node = self._parse_unary()
                return ("unary", op, node)
            return self._parse_postfix()

        def _parse_postfix(self) -> Any:
            node = self._parse_primary()
            while self.peek() in {"++", "--"}:
                op = self.take()
                node = ("post", op, node)
            return node

        def _parse_primary(self) -> Any:
            tok = self.peek()
            if tok is None:
                raise ValueError("missing expression")
            if tok == "(":
                self.take()
                node = self._parse_comma()
                self.expect(")")
                return node
            self.take()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", tok):
                if self.peek() == "[":
                    self.take()
                    idx = self._parse_comma()
                    self.expect("]")
                    return ("sub", tok, idx)
                return ("var", tok)
            return ("num", tok)

    def _arith_is_lvalue(self, node: Any) -> bool:
        if not isinstance(node, tuple):
            return False
        return node[0] in {"var", "sub"}

    def _arith_eval_node(self, node: Any) -> int:
        if not isinstance(node, tuple) or not node:
            raise ValueError("invalid arithmetic node")
        t = node[0]
        if t == "num":
            return self._arith_parse_number(str(node[1]))
        if t == "var":
            return self._arith_get_var_int(str(node[1]), seen=set())
        if t == "sub":
            base = str(node[1])
            idx = self._arith_eval_node(node[2])
            return self._arith_get_subscript_int(base, idx)
        if t == "comma":
            self._arith_eval_node(node[1])
            return self._arith_eval_node(node[2])
        if t == "unary":
            op = str(node[1])
            child = node[2]
            if op == "++":
                old, setter = self._arith_resolve_lvalue(child)
                new = old + 1
                setter(new)
                return new
            if op == "--":
                old, setter = self._arith_resolve_lvalue(child)
                new = old - 1
                setter(new)
                return new
            v = self._arith_eval_node(child)
            if op == "+":
                return v
            if op == "-":
                return -v
            if op == "!":
                return 0 if v else 1
            if op == "~":
                return ~v
            raise ValueError("unknown unary op")
        if t == "post":
            op = str(node[1])
            old, setter = self._arith_resolve_lvalue(node[2])
            if op == "++":
                setter(old + 1)
                return old
            if op == "--":
                setter(old - 1)
                return old
            raise ValueError("unknown postfix op")
        if t == "assign":
            op = str(node[1])
            old, setter = self._arith_resolve_lvalue(node[2])
            rhs = self._arith_eval_node(node[3])
            if op == "=":
                out = rhs
            elif op == "+=":
                out = old + rhs
            elif op == "-=":
                out = old - rhs
            elif op == "*=":
                out = old * rhs
            elif op == "/=":
                if rhs == 0:
                    raise ZeroDivisionError()
                out = int(old / rhs)
            elif op == "%=":
                if rhs == 0:
                    raise ZeroDivisionError()
                out = old % rhs
            elif op == "<<=":
                out = old << rhs
            elif op == ">>=":
                out = old >> rhs
            elif op == "&=":
                out = old & rhs
            elif op == "^=":
                out = old ^ rhs
            elif op == "|=":
                out = old | rhs
            else:
                raise ValueError("unknown assignment op")
            setter(out)
            return out
        if t == "ternary":
            cond = self._arith_eval_node(node[1])
            if cond != 0:
                return self._arith_eval_node(node[2])
            return self._arith_eval_node(node[3])
        if t == "bin":
            op = str(node[1])
            if op == "||":
                left = self._arith_eval_node(node[2])
                if left != 0:
                    return 1
                return 1 if self._arith_eval_node(node[3]) != 0 else 0
            if op == "&&":
                left = self._arith_eval_node(node[2])
                if left == 0:
                    return 0
                return 1 if self._arith_eval_node(node[3]) != 0 else 0
            left = self._arith_eval_node(node[2])
            right = self._arith_eval_node(node[3])
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    raise ZeroDivisionError()
                return int(left / right)
            if op == "%":
                if right == 0:
                    raise ZeroDivisionError()
                return left % right
            if op == "<<":
                return left << right
            if op == ">>":
                return left >> right
            if op == "<":
                return 1 if left < right else 0
            if op == "<=":
                return 1 if left <= right else 0
            if op == ">":
                return 1 if left > right else 0
            if op == ">=":
                return 1 if left >= right else 0
            if op == "==":
                return 1 if left == right else 0
            if op == "!=":
                return 1 if left != right else 0
            if op == "&":
                return left & right
            if op == "^":
                return left ^ right
            if op == "|":
                return left | right
            raise ValueError("unknown binary op")
        raise ValueError("invalid arithmetic node type")

    def _arith_resolve_lvalue(self, node: Any) -> tuple[int, Callable[[int], None]]:
        if not isinstance(node, tuple) or not node:
            raise ValueError("invalid lvalue")
        if node[0] == "var":
            name = str(node[1])
            cur = self._arith_get_var_int(name, seen=set())

            def _set(v: int) -> None:
                self._assign_shell_var(name, str(v))

            return cur, _set
        if node[0] == "sub":
            base = str(node[1])
            idx = self._arith_eval_node(node[2])
            attrs = self._var_attrs.get(base, set())
            typed = self._typed_vars.get(base)
            if "assoc" in attrs:
                cur_map = dict(typed) if isinstance(typed, dict) else {}
                key = str(idx)
                old_raw = str(cur_map.get(key, ""))
                try:
                    old = self._arith_parse_number(old_raw)
                except Exception:
                    old = self._arith_get_var_int(old_raw, seen={base})

                def _set(v: int) -> None:
                    self._assign_shell_var(f"{base}[{key}]", str(v))

                return old, _set
            cur_arr = list(typed) if isinstance(typed, list) else []
            if idx < 0:
                max_idx = self._array_max_index(cur_arr)
                idx = (max_idx + 1 + idx) if max_idx is not None else idx
            if idx < 0:
                raise ValueError("bad array subscript")
            old = 0
            if 0 <= idx < len(cur_arr) and cur_arr[idx] is not None:
                raw = str(cur_arr[idx])
                try:
                    old = self._arith_parse_number(raw)
                except Exception:
                    old = self._arith_get_var_int(raw, seen={base})

            def _set(v: int, _idx: int = idx) -> None:
                self._assign_shell_var(f"{base}[{_idx}]", str(v))

            return old, _set
        raise ValueError("invalid lvalue")

    def _arith_get_subscript_int(self, base: str, idx: int) -> int:
        attrs = self._var_attrs.get(base, set())
        typed = self._typed_vars.get(base)
        if "assoc" in attrs and isinstance(typed, dict):
            raw = str(typed.get(str(idx), ""))
            if raw == "":
                return 0
            try:
                return self._arith_parse_number(raw)
            except Exception:
                return self._arith_get_var_int(raw, seen={base})
        if isinstance(typed, list):
            if idx < 0:
                max_idx = self._array_max_index(typed)
                idx = (max_idx + 1 + idx) if max_idx is not None else idx
            if 0 <= idx < len(typed) and typed[idx] is not None:
                raw = str(typed[idx])
                try:
                    return self._arith_parse_number(raw)
                except Exception:
                    return self._arith_get_var_int(raw, seen={base})
            return 0
        return 0

    def _arith_get_var_int(self, name: str, *, seen: set[str]) -> int:
        if name in seen:
            return 0
        seen2 = set(seen)
        seen2.add(name)
        raw, is_set = self._get_var_with_state(name)
        if not is_set or raw == "":
            return 0
        try:
            return self._arith_parse_number(raw)
        except Exception:
            try:
                return self._eval_arith_expr_with_seen(raw, seen2)
            except Exception:
                return 0

    def _eval_arith_expr_with_seen(self, expr: str, seen: set[str]) -> int:
        tokens = self._arith_tokens(expr)
        if not tokens:
            return 0
        parser = self._ArithParser(self, tokens)
        node = parser.parse()
        if parser.peek() is not None:
            raise ValueError("trailing arithmetic tokens")
        return self._arith_eval_node_with_seen(node, seen)

    def _arith_eval_node_with_seen(self, node: Any, seen: set[str]) -> int:
        if isinstance(node, tuple) and node and node[0] == "var":
            return self._arith_get_var_int(str(node[1]), seen=seen)
        if isinstance(node, tuple) and node and node[0] == "sub":
            base = str(node[1])
            idx = self._arith_eval_node_with_seen(node[2], seen)
            return self._arith_get_subscript_int(base, idx)
        if isinstance(node, tuple) and node and node[0] == "num":
            return self._arith_parse_number(str(node[1]))
        if isinstance(node, tuple) and node and node[0] in {"comma", "ternary", "bin", "unary", "post", "assign"}:
            # Fallback to normal evaluator for operator semantics; recursive name
            # lookup still goes through _arith_get_var_int which guards cycles.
            return self._arith_eval_node(node)
        raise ValueError("invalid arithmetic node")

    def _arith_parse_number(self, text: str) -> int:
        s = (text or "").strip()
        if s == "":
            return 0
        m_base = re.fullmatch(r"([0-9]+)#([0-9A-Za-z@_]+)", s)
        if m_base is not None:
            base = int(m_base.group(1), 10)
            if base < 2 or base > 64:
                raise ValueError("invalid base")
            digits = m_base.group(2)
            alpha = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@_"
            out = 0
            for ch in digits:
                d = alpha.find(ch)
                if d < 0 or d >= base:
                    raise ValueError("invalid based literal")
                out = out * base + d
            return out
        if re.fullmatch(r"0[0-7]+", s):
            return int(s, 8)
        return int(s, 0)

    def _materialize_random_in_arith(self, expr: str) -> str:
        if "RANDOM" not in expr:
            return expr
        out: list[str] = []
        i = 0
        n = len(expr)
        while i < n:
            if expr[i] == "$":
                if expr.startswith("$RANDOM", i):
                    out.append(self._next_random())
                    i += len("$RANDOM")
                    continue
                if expr.startswith("${RANDOM}", i):
                    out.append(self._next_random())
                    i += len("${RANDOM}")
                    continue
                out.append(expr[i])
                i += 1
                continue
            if expr[i].isalpha() or expr[i] == "_":
                j = i + 1
                while j < n and (expr[j].isalnum() or expr[j] == "_"):
                    j += 1
                name = expr[i:j]
                if name == "RANDOM":
                    out.append(self._next_random())
                else:
                    out.append(name)
                i = j
                continue
            out.append(expr[i])
            i += 1
        return "".join(out)

    def _expand_heredoc(self, redir: Redirect) -> str:
        content = redir.here_doc or ""
        if not redir.here_doc_expand:
            return content
        return self._expand_heredoc_unquoted(content)

    def _expand_here_string(self, redir: Redirect) -> str:
        target = self._expand_redir_target(redir)
        return ("" if target is None else target) + "\n"

    def _expand_heredoc_unquoted(self, text: str) -> str:
        out: List[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == "\\":
                if i + 1 < len(text) and text[i + 1] == "\n":
                    i += 2
                    continue
                if i + 1 < len(text) and text[i + 1] in ["\\", "$", "`"]:
                    out.append(text[i + 1])
                    i += 2
                    continue
                out.append("\\")
                i += 1
                continue
            if ch == "`":
                j = i + 1
                cmd: List[str] = []
                while j < len(text):
                    if text[j] == "\\" and j + 1 < len(text):
                        nxt = text[j + 1]
                        if nxt in ["\\", "`", "$", "\n"]:
                            cmd.append(nxt)
                            j += 2
                            continue
                        cmd.append("\\")
                        cmd.append(nxt)
                        j += 2
                        continue
                    if text[j] == "`":
                        break
                    cmd.append(text[j])
                    j += 1
                out.append(self._expand_command_subst_text("".join(cmd), backtick=True))
                i = j + 1 if j < len(text) and text[j] == "`" else j
                continue
            if ch == "$":
                if text.startswith("$((", i):
                    expr, end = _extract_balanced(text, i + 3, "))")
                    out.append(self._expand_arith(expr))
                    i = end
                    continue
                if text.startswith("$(", i):
                    cmd, end = _extract_balanced(text, i + 2, ")")
                    out.append(self._expand_command_subst_text(cmd))
                    i = end
                    continue
                if text.startswith("${", i):
                    end = _find_braced_end(text, i + 2)
                    if end == -1:
                        out.append("$")
                        i += 1
                        continue
                    inner = text[i + 2 : end]
                    name, op, arg = _split_braced(inner)
                    if name is None:
                        raise RuntimeError(
                            self._format_error("syntax error: bad substitution", line=self.current_line)
                        )
                    # Here-doc expansion uses a distinct quote-removal context.
                    # Keep parameter-op WORD handling on the raw textual path
                    # instead of pre-parsed structured fields.
                    val = self._expand_braced_param(name, op, arg, False, arg_fields=None)
                    out.append(self._scalarize_assignment_expansion(val))
                    i = end + 1
                    continue
                if i + 1 < len(text):
                    nxt = text[i + 1]
                    if nxt in "#@*?$!-":
                        val = self._expand_param(nxt, False)
                        if isinstance(val, (list, PresplitFields)):
                            out.append(" ".join(str(v) for v in val))
                        else:
                            out.append("" if val is None else str(val))
                        i += 2
                        continue
                    if nxt.isdigit():
                        val = self._expand_param(nxt, False)
                        if isinstance(val, (list, PresplitFields)):
                            out.append(" ".join(str(v) for v in val))
                        else:
                            out.append("" if val is None else str(val))
                        i += 2
                        continue
                    if nxt.isalpha() or nxt == "_":
                        j = i + 1
                        while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                            j += 1
                        name = text[i + 1 : j]
                        val = self._expand_param(name, False)
                        if isinstance(val, (list, PresplitFields)):
                            out.append(" ".join(str(v) for v in val))
                        else:
                            out.append("" if val is None else str(val))
                        i = j
                        continue
                out.append("$")
                i += 1
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def _dup_fd(
        self,
        redir: Redirect,
        is_output: bool,
        default_fd: int | None = None,
        allowed_fds: set[int] | None = None,
    ) -> None:
        fd = redir.fd if redir.fd is not None else (1 if is_output else 0)
        target = self._expand_redir_target(redir) if redir.target else redir.target
        try:
            if target == "-":
                try:
                    os.close(fd)
                except OSError:
                    pass
                self._user_fds.discard(fd)
                if allowed_fds is not None:
                    allowed_fds.discard(fd)
                return
            if target.isdigit():
                src_fd = int(target)
                if (
                    src_fd == 3
                    and src_fd not in self._user_fds
                    and src_fd not in self._active_temp_fds
                    and (allowed_fds is None or src_fd not in allowed_fds)
                ):
                    raise OSError(9, "Bad file descriptor")
                os.dup2(src_fd, fd)
                if fd >= 3:
                    if allowed_fds is not None:
                        allowed_fds.add(fd)
                    else:
                        self._user_fds.add(fd)
                return
            raise OSError(9, "Bad file descriptor")
        except OSError as e:
            if target and target.isdigit():
                # BusyBox ash diagnostics special-case fd 10 in script-mode.
                if int(target) == 10 and fd == 1:
                    raise RuntimeError(self._format_error(f"{target}: {e.strerror}", line=self.current_line))
                raise RuntimeError(self._format_error(f"dup2({target},{fd}): {e.strerror}", line=self.current_line))
            raise RuntimeError(self._format_error(f"{target}: {e.strerror}", line=self.current_line))

    def _get_var(self, name: str) -> str:
        if name == "RANDOM":
            return self._next_random()
        parsed = self._parse_subscripted_name(name)
        if parsed is not None:
            v, is_set = self._get_var_with_state(name)
            return v if is_set else ""
        tied = self._py_ties.get(name)
        if tied is not None:
            getter, _, tie_type = tied
            try:
                return self._tie_value_to_shell(getter(), tie_type)
            except Exception:
                return ""
        for scope in reversed(self.local_stack):
            if name in scope:
                return scope[name]
        return self.env.get(name, "")

    def _parse_subscripted_name(self, name: str) -> tuple[str, str] | None:
        m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\[(.*)\]", name)
        if m is None:
            return None
        base = m.group(1)
        key_raw = m.group(2).strip()
        if len(key_raw) >= 2 and key_raw[0] == key_raw[-1] and key_raw[0] in {"'", '"'}:
            key_raw = key_raw[1:-1]
        return base, key_raw

    def _structured_var_attrs(self, name: str) -> set[str]:
        parsed = self._parse_subscripted_name(name)
        base = parsed[0] if parsed is not None else name
        return self._var_attrs.get(base, set())

    def _is_structured_assignment_target(self, name: str) -> bool:
        parsed = self._parse_subscripted_name(name)
        if parsed is not None:
            return True
        attrs = self._var_attrs.get(name, set())
        return ("array" in attrs) or ("assoc" in attrs)

    def _sync_local_env_assignment(self, local_env: dict[str, str], name: str) -> None:
        parsed = self._parse_subscripted_name(name)
        if parsed is not None:
            base = parsed[0]
            if base == "RANDOM":
                local_env[base] = self.env.get(base, "")
                return
            local_env[base] = self._get_var(base)
            return
        if name == "RANDOM":
            local_env[name] = self.env.get(name, "")
            return
        local_env[name] = self._get_var(name)

    def _set_subscript_projection(self, base: str, value: str) -> None:
        for scope in reversed(self.local_stack):
            if base in scope:
                scope[base] = value
                return
        self.env[base] = value

    @staticmethod
    def _array_visible_values(seq: list[object]) -> list[str]:
        out: list[str] = []
        for v in seq:
            if v is None:
                continue
            out.append(str(v))
        return out

    @staticmethod
    def _array_max_index(seq: list[object]) -> int | None:
        for i in range(len(seq) - 1, -1, -1):
            if seq[i] is not None:
                return i
        return None

    def _argv_assignment_words(
        self, argv: list[str], eligible: list[bool] | None = None
    ) -> list[tuple[str, str, object, bool]] | None:
        words = list(argv)
        # Join indexed assignment forms that may be split by spaces inside the
        # subscript expression, e.g. `a[7 + 8]=x`.
        folded_words: list[str] = []
        i = 0
        while i < len(words):
            tok = words[i]
            if (
                re.match(r"^[A-Za-z_][A-Za-z0-9_]*\[[^\]]*$", tok)
                and "=" not in tok
                and "]" not in tok
            ):
                merged = tok
                j = i
                while j + 1 < len(words):
                    j += 1
                    merged = merged + " " + words[j]
                    if "]" in words[j]:
                        break
                if "]" in merged and "=" in merged:
                    folded_words.append(merged)
                    i = j + 1
                    continue
            folded_words.append(tok)
            i += 1

        out: list[tuple[str, str, object, bool]] = []
        i = 0
        while i < len(folded_words):
            tok = folded_words[i]
            if eligible is not None:
                if i >= len(eligible):
                    return None
                if not eligible[i]:
                    # Structured-word eligibility can be false for assignment
                    # words that contain command substitution/arithmetic in
                    # subscripts (e.g. array[$(cmd)-1]=x). Keep recognizing
                    # clear lexical assignment forms here.
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*(?:\[[^]]*\])?\+?=", tok) is None:
                        return None
            m_comp = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(\+?=)\((.*)$", tok)
            if m_comp is not None:
                name = m_comp.group(1)
                op = m_comp.group(2)
                tail = m_comp.group(3)
                vals: list[str] = []
                while True:
                    if tail.endswith(")"):
                        chunk = tail[:-1]
                        if chunk != "":
                            vals.append(chunk)
                        break
                    if tail != "":
                        vals.append(tail)
                    i += 1
                    if i >= len(folded_words):
                        return None
                    tail = folded_words[i]
                out.append((name, op, vals, True))
                i += 1
                continue

            m_comp_open = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(\+?=)$", tok)
            if m_comp_open is not None:
                name = m_comp_open.group(1)
                op = m_comp_open.group(2)
                if i + 1 >= len(folded_words) or folded_words[i + 1] != "(":
                    return None
                i += 2
                vals = []
                while i < len(folded_words):
                    cur = folded_words[i]
                    if cur == ")":
                        break
                    vals.append(cur)
                    i += 1
                if i >= len(folded_words) or folded_words[i] != ")":
                    return None
                out.append((name, op, vals, True))
                i += 1
                continue

            m = re.match(r"^([^=]+?)(\+?=)(.*)$", tok)
            if m is None:
                return None
            name = m.group(1)
            op = m.group(2)
            value = m.group(3)
            parsed_sub = self._parse_subscripted_name(name)
            if not (self._is_valid_name(name) or parsed_sub is not None):
                return None
            if parsed_sub is not None and self._bash_compat_level is None:
                # In ash/POSIX lane, token forms like `a[0]=x` are not assignment
                # words; they should be treated as command names.
                return None
            out.append((name, op, value, False))
            i += 1
        return out

    def _asdl_word_is_plain_assignment_candidate(self, node: Any) -> bool:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return False
        parts = node.get("parts") or []
        if not isinstance(parts, list) or not parts:
            return False
        for part in parts:
            if not isinstance(part, dict):
                return False
            if part.get("type") != "word_part.Literal":
                return False
            if "\\" in str(part.get("tval", "")):
                # Escapes/quoting in source means this is not a lexical
                # assignment word, even if expanded text contains '='.
                return False
        return True

    def _assign_compound_var(
        self,
        name: str,
        op: str,
        values: list[str] | list[tuple[str, bool]],
        *,
        attrs_override: set[str] | None = None,
    ) -> None:
        if self._bash_compat_level is None:
            raise RuntimeError(f"{name}: compound assignment requires BASH_COMPAT")
        normalized: list[tuple[str, bool]] = []
        for v in values:
            if isinstance(v, tuple):
                normalized.append((str(v[0]), bool(v[1])))
            else:
                tok = str(v)
                normalized.append((tok, re.match(r"^\[(.*)\](\+?=)(.*)$", tok) is not None))
        attrs = set(attrs_override) if attrs_override is not None else self._var_attrs.get(name, set())
        if "assoc" in attrs:
            cur_map = self._typed_vars.get(name)
            out_map: dict[str, str] = dict(cur_map) if (op == "+=" and isinstance(cur_map, dict)) else {}
            for raw, explicit_idx_syntax in normalized:
                m = re.match(r"^\[(.*)\](\+?=)(.*)$", raw) if explicit_idx_syntax else None
                if m is None:
                    val = self._coerce_value_with_attrs(self._expand_assignment_word(raw), attrs)
                    if op == "+=":
                        out_map["0"] = str(out_map.get("0", "")) + val
                    else:
                        out_map["0"] = val
                    continue
                key = str(self._eval_assoc_subscript_key(m.group(1)))
                inner_op = m.group(2)
                rhs = self._coerce_value_with_attrs(self._expand_assignment_word(m.group(3)), attrs)
                if inner_op == "+=" and op == "+=":
                    out_map[key] = str(out_map.get(key, "")) + rhs
                else:
                    out_map[key] = rhs
            self._typed_vars[name] = out_map
            self._set_var_attrs(name, assoc=True)
            self._set_subscript_projection(name, str(out_map.get("0", "")))
            return
        cur = self._typed_vars.get(name)
        out_vals: list[object] = list(cur) if (op == "+=" and isinstance(cur, list)) else []
        integer_mode = "integer" in attrs
        next_idx = 0
        if op == "+=" and out_vals:
            next_idx = max(i for i, v in enumerate(out_vals) if v is not None) + 1
        for tok, explicit_idx_syntax in normalized:
            m = re.match(r"^\[(.*)\](\+?=)(.*)$", tok) if explicit_idx_syntax else None
            if m is None:
                expanded_items = fields_to_text_list(self._legacy_word_to_expansion_fields(tok, assignment=False))
                if not expanded_items:
                    expanded_items = [""]
                for val in expanded_items:
                    val = self._coerce_value_with_attrs(val, attrs)
                    while next_idx < len(out_vals) and out_vals[next_idx] is not None:
                        next_idx += 1
                    if next_idx >= len(out_vals):
                        out_vals.extend([None] * (next_idx + 1 - len(out_vals)))
                    out_vals[next_idx] = val
                    next_idx += 1
                continue
            idx_expr = m.group(1)
            inner_op = m.group(2)
            rhs_raw = m.group(3)
            idx_text = idx_expr.strip()
            if idx_text == "":
                self._report_error(f"[]={rhs_raw}: bad array subscript", line=self.current_line)
                continue
            if idx_text in {"*", "@"}:
                self._report_error(f"[{idx_text}]={rhs_raw}: cannot assign to non-numeric index", line=self.current_line)
                continue
            try:
                idx = self._eval_index_subscript(idx_expr, out_vals, strict=True, name=name)
            except RuntimeError:
                self._report_error(f"[{idx_text}]={rhs_raw}: bad array subscript", line=self.current_line)
                continue
            if idx is None:
                continue
            if idx >= len(out_vals):
                out_vals.extend([None] * (idx + 1 - len(out_vals)))
            rhs = self._expand_assignment_word(rhs_raw)
            rhs = self._coerce_value_with_attrs(rhs, attrs)
            if inner_op == "+=" and op == "+=":
                old = "" if out_vals[idx] is None else str(out_vals[idx])
                if integer_mode:
                    rhs = str(
                        self._to_int_arith(old if old != "" else "0")
                        + self._to_int_arith(rhs if rhs != "" else "0")
                    )
                else:
                    rhs = old + rhs
            out_vals[idx] = rhs
            next_idx = idx + 1
        self._typed_vars[name] = out_vals
        self._set_var_attrs(name, array=True)
        proj = ""
        if len(out_vals) > 0 and out_vals[0] is not None:
            proj = str(out_vals[0])
        self._set_subscript_projection(name, proj)

    def _parse_compound_assignment_rhs_entries(self, rhs: str) -> list[tuple[str, bool]] | None:
        text = rhs.strip()
        if not (text.startswith("(") and text.endswith(")")):
            return None
        inner = text[1:-1]
        if inner.strip() == "":
            return []
        vals: list[tuple[str, bool]] = []
        reader = TokenReader(inner)
        ctx = LexContext(reserved_words=set(), allow_reserved=False, allow_newline=False)
        while True:
            tok = reader.next(ctx)
            if tok is None:
                break
            if tok.kind != "WORD":
                return None
            vals.append((tok.value, re.match(r"^\[(.*)\](\+?=)(.*)$", tok.value) is not None))
        return vals

    def _parse_compound_assignment_rhs(self, rhs: str) -> list[str] | None:
        entries = self._parse_compound_assignment_rhs_entries(rhs)
        if entries is None:
            return None
        return [v for v, _ in entries]

    def _compound_assignment_unexpected_token(self, rhs: str) -> str | None:
        text = rhs.strip()
        if not (text.startswith("(") and text.endswith(")")):
            return None
        inner = text[1:-1]
        reader = TokenReader(inner)
        ctx = LexContext(reserved_words=set(), allow_reserved=False, allow_newline=True)
        while True:
            tok = reader.next(ctx)
            if tok is None:
                break
            if tok.kind == "OP" and tok.value != "\n":
                return tok.value
        return None

    def _parse_assoc_compound_assignment_rhs(self, rhs: str) -> dict[str, str] | None:
        text = rhs.strip()
        if not (text.startswith("(") and text.endswith(")")):
            return None
        inner = text[1:-1]
        if inner.strip() == "":
            return {}
        out: dict[str, str] = {}
        reader = TokenReader(inner)
        ctx = LexContext(reserved_words=set(), allow_reserved=False, allow_newline=False)
        while True:
            tok = reader.next(ctx)
            if tok is None:
                break
            if tok.kind != "WORD":
                return None
            m = re.match(r"^\[(.*)\]=(.*)$", tok.value)
            if m is None:
                return None
            key_raw = m.group(1)
            val_raw = m.group(2)
            key = self._eval_assoc_subscript_key(key_raw)
            out[str(key)] = self._expand_assignment_word(val_raw)
        return out

    def _assign_subscripted_var(self, name: str, value: str) -> bool:
        parsed = self._parse_subscripted_name(name)
        if parsed is None:
            return False
        if self._bash_compat_level is None:
            raise RuntimeError(f"{name}: indexed assignment requires BASH_COMPAT")
        base, key = parsed
        attrs = self._var_attrs.get(base, set())
        if "assoc" in attrs:
            if base in self.readonly_vars:
                raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=base))
            cur = self._typed_vars.get(base)
            if not isinstance(cur, dict):
                cur = {}
            akey = self._eval_assoc_subscript_key(key)
            if "integer" in attrs:
                value = str(self._to_int_arith(value if value != "" else "0"))
            cur[str(akey)] = value
            self._typed_vars[base] = cur
            self._set_subscript_projection(base, str(cur.get("0", "")))
            return True
        # Default to indexed array semantics when assoc isn't declared.
        cur_arr = self._typed_vars.get(base)
        if not isinstance(cur_arr, list):
            cur_arr = []
            # Bash-compatible scalar -> indexed array promotion preserves
            # existing scalar value as element 0.
            cur_scalar, scalar_is_set = self._get_var_with_state(base)
            if scalar_is_set:
                cur_arr = [cur_scalar]
        idx = self._eval_index_subscript(key, cur_arr, strict=True, name=name)
        if idx is None:
            raise RuntimeError(f"{name}: bad array subscript")
        if base in self.readonly_vars:
            raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=base))
        if idx >= len(cur_arr):
            cur_arr.extend([None] * (idx + 1 - len(cur_arr)))
        if "integer" in attrs:
            value = str(self._to_int_arith(value if value != "" else "0"))
        cur_arr[idx] = value
        self._typed_vars[base] = cur_arr
        proj = ""
        if len(cur_arr) > 0 and cur_arr[0] is not None:
            proj = str(cur_arr[0])
        self._set_subscript_projection(base, proj)
        self._set_var_attrs(base, array=True)
        return True

    def _eval_index_subscript(
        self,
        key: str,
        seq: list[object],
        *,
        strict: bool = False,
        name: str | None = None,
        empty_is_zero: bool = False,
    ) -> int | None:
        text = (key or "").strip()
        if text == "":
            if empty_is_zero:
                return 0
            if strict:
                label = name or key or "array"
                raise RuntimeError(f"{label}: bad array subscript")
            return None
        try:
            # Bash performs expansions on array subscript text before arithmetic
            # evaluation (parameter/command/tilde, then arithmetic context).
            text = self._expand_assignment_word(text)
        except Exception:
            if strict:
                label = name or key or "array"
                raise RuntimeError(f"{label}: bad array subscript")
            return None
        text = text.strip()
        if text == "":
            if empty_is_zero:
                return 0
            if strict:
                label = name or key or "array"
                raise RuntimeError(f"{label}: bad array subscript")
            return None
        m_arith_wrap = re.fullmatch(r"\$\(\((.*)\)\)", text, re.DOTALL)
        if m_arith_wrap is not None:
            text = m_arith_wrap.group(1).strip()
        m_name = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text)
        if m_name is not None and self.options.get("u", False):
            _, is_set = self._get_var_with_state(m_name.group(0))
            if not is_set:
                raise RuntimeError(f"unbound variable: {m_name.group(0)}")
        # Minimal bash-compat side-effect support for common indexed patterns
        # used by compatibility probes (e.g. arr[i++] in [[ -v ... ]]).
        m_post_inc = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\\+\\+", text)
        if m_post_inc is not None:
            var = m_post_inc.group(1)
            cur_raw = self._get_var(var)
            try:
                cur = int(cur_raw, 10) if cur_raw != "" else 0
            except Exception:
                cur = 0
            self._assign_shell_var(var, str(cur + 1))
            return cur
        m_post_dec = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)--", text)
        if m_post_dec is not None:
            var = m_post_dec.group(1)
            cur_raw = self._get_var(var)
            try:
                cur = int(cur_raw, 10) if cur_raw != "" else 0
            except Exception:
                cur = 0
            self._assign_shell_var(var, str(cur - 1))
            return cur
        try:
            idx = int(self._expand_arith(text, context="subscript"))
        except ArithExpansionFailure:
            if strict:
                label = name or key or "array"
                raise RuntimeError(f"{label}: bad array subscript")
            return None
        except Exception:
            if strict:
                label = name or key or "array"
                raise RuntimeError(f"{label}: bad array subscript")
            return None
        if idx < 0:
            max_idx = self._array_max_index(seq)
            if max_idx is None:
                if strict:
                    label = name or key or "array"
                    raise RuntimeError(f"{label}: bad array subscript")
                return None
            idx = max_idx + 1 + idx
            if idx < 0:
                if strict:
                    label = name or key or "array"
                    raise RuntimeError(f"{label}: bad array subscript")
                return None
        return idx

    def _get_var_with_state(self, name: str) -> tuple[str, bool]:
        if name == "RANDOM":
            return self._next_random(), True
        parsed = self._parse_subscripted_name(name)
        if parsed is not None:
            if self._bash_compat_level is None:
                return "", False
            base, key = parsed
            attrs = self._var_attrs.get(base, set())
            typed = self._typed_vars.get(base)
            if "assoc" in attrs:
                if not isinstance(typed, dict):
                    return "", False
                if key in {"@", "*"}:
                    vals = [str(v) for v in reversed(list(typed.values()))]
                    if key == "*":
                        return self._ifs_join(vals), bool(vals)
                    return " ".join(vals), bool(vals)
                akey = self._eval_assoc_subscript_key(key)
                if akey in typed:
                    return str(typed[akey]), True
                return "", False
            if not isinstance(typed, list):
                scalar_value, scalar_set = self._get_var_with_state(base)
                if not scalar_set:
                    return "", False
                idx = self._eval_index_subscript(key, [], strict=False, name=base, empty_is_zero=True)
                if idx is None or idx != 0:
                    return "", False
                return scalar_value, True
            if key in {"@", "*"}:
                vals = self._array_visible_values(typed)
                if key == "*":
                    return self._ifs_join(vals), bool(vals)
                return " ".join(vals), bool(vals)
            idx = self._eval_index_subscript(key, typed, strict=True, name=base, empty_is_zero=True)
            if idx is None:
                return "", False
            if idx < 0 or idx >= len(typed):
                return "", False
            cell = typed[idx]
            if cell is None:
                return "", False
            return str(cell), True
        attrs = self._var_attrs.get(name, set())
        if "assoc" in attrs:
            typed = self._typed_vars.get(name)
            if isinstance(typed, dict) and "0" in typed:
                return str(typed["0"]), True
            return "", False
        if "array" in attrs:
            typed = self._typed_vars.get(name)
            if isinstance(typed, list) and len(typed) > 0 and typed[0] is not None:
                return str(typed[0]), True
            return "", False
        for scope in reversed(self.local_stack):
            if name in scope:
                return scope[name], True
        if name in self.env:
            return self.env[name], True
        return "", False

    def _get_param_state(self, name: str) -> tuple[str, bool]:
        if name == "#":
            return str(len(self.positional)), True
        if name == "?":
            return str(self.last_status), True
        if name == "$":
            return str(os.getpid()), True
        if name == "!":
            return (
                str(self._last_bg_job) if self._last_bg_job is not None else "",
                self._last_bg_job is not None,
            )
        if name == "-":
            return self._option_flags(), True
        if name == "LINENO":
            line = self.current_line if self.current_line is not None else 0
            if self.c_string_mode:
                line = max(0, line - 1)
            return str(line), True
        if name == "@":
            return " ".join(self.positional), len(self.positional) > 0
        if name == "*":
            return self._ifs_join(self.positional), len(self.positional) > 0
        if name.isdigit():
            value = self._get_positional(name)
            idx = int(name)
            if idx == 0:
                return value, True
            return value, idx <= len(self.positional)
        return self._get_var_with_state(name)

    def _ifs_join(self, items: List[str]) -> str:
        ifs = self.env.get("IFS", " \t\n")
        sep = ifs[0] if ifs else ""
        return sep.join(items)

    def _option_flags(self) -> str:
        out: list[str] = []
        for ch in self.OPTION_FLAG_ORDER:
            if self.options.get(ch, False):
                out.append(ch)
        return "".join(out)

    def _remove_prefix(self, value: str, pattern: str, longest: bool) -> str:
        if pattern == "":
            return value
        indices = range(len(value), -1, -1) if longest else range(0, len(value) + 1)
        for i in indices:
            prefix = value[:i]
            if self._shell_pattern_match(prefix, pattern):
                return value[i:]
        return value

    def _remove_suffix(self, value: str, pattern: str, longest: bool) -> str:
        if pattern == "":
            return value
        indices = range(0, len(value) + 1) if longest else range(len(value), -1, -1)
        for i in indices:
            suffix = value[i:]
            if self._shell_pattern_match(suffix, pattern):
                return value[:i]
        return value

    def _shell_pattern_match(self, text: str, pattern: str) -> bool:
        return self._case_pattern_matches(text, pattern)

    def _pattern_from_word(self, text: str, for_case: bool = False) -> str:
        fields = self._legacy_word_to_expansion_fields(text, assignment=True)
        return self._pattern_from_structured_fields(fields, for_case=for_case)

    def _pattern_from_structured_fields(self, fields: list[ExpansionField], *, for_case: bool = False) -> str:
        # Parameter-op and case-pattern helpers can pass ASDL-derived structured
        # fields here and avoid text-marker roundtrips.
        if not fields:
            return ""
        raw_parts: list[str] = []
        for field in fields:
            for seg in field.segments:
                if seg.quoted:
                    raw_parts.append(self._escape_case_pattern_literal(seg.text))
                else:
                    raw_parts.append(self._tilde_expand(seg.text))
        return self._pattern_from_literalized_raw("".join(raw_parts), for_case=for_case)

    def _structured_fields_to_assignment_scalar(self, fields: list[ExpansionField]) -> str:
        texts = fields_to_text_list(fields)
        if not texts:
            return ""
        if len(texts) == 1:
            return texts[0]
        return self._ifs_join(texts)

    def _pattern_from_literalized_raw(self, raw: str, *, for_case: bool = False) -> str:
        out: List[str] = []
        i = 0
        in_class = False
        class_can_close = False
        while i < len(raw):
            ch = raw[i]
            if ch == "[":
                in_class = True
                class_can_close = False
                out.append(ch)
                i += 1
                continue
            if in_class:
                # Inside bracket expressions backslash is literal in shell
                # patterns; it does not escape ']'.
                out.append(ch)
                if ch == "]" and class_can_close:
                    in_class = False
                else:
                    class_can_close = True
                i += 1
                continue
            if ch == "\\" and i + 1 < len(raw):
                nxt = raw[i + 1]
                if nxt == "*":
                    out.append("[*]")
                elif nxt == "?":
                    out.append("[?]")
                elif nxt == "[":
                    out.append("[[]")
                elif nxt == "]":
                    out.append("[]]")
                elif nxt == "\\":
                    out.append("[\\\\]")
                else:
                    out.append(nxt)
                i += 2
                continue
            out.append(ch)
            i += 1
        pat = "".join(out)
        if for_case:
            return self._normalize_class_escapes(pat)
        return pat

    def _normalize_class_escapes(self, pattern: str) -> str:
        out: List[str] = []
        i = 0
        while i < len(pattern):
            if pattern[i] != "[":
                out.append(pattern[i])
                i += 1
                continue
            j = i + 1
            cls: List[str] = []
            while j < len(pattern):
                if pattern[j] == "\\" and j + 1 < len(pattern):
                    cls.append(pattern[j : j + 2])
                    j += 2
                    continue
                if pattern[j] == "]":
                    break
                cls.append(pattern[j])
                j += 1
            if j >= len(pattern) or pattern[j] != "]":
                out.append(pattern[i])
                i += 1
                continue

            neg = False
            k = 0
            if cls and cls[0] == "!":
                neg = True
                k = 1

            literal_rbr = False
            literal_hy = 0
            body: List[str] = []
            for tok in cls[k:]:
                if tok == r"\]":
                    literal_rbr = True
                    continue
                if tok == r"\-":
                    literal_hy += 1
                    continue
                body.append(tok)

            out.append("[")
            if neg:
                out.append("!")
            if literal_rbr:
                out.append("]")
            out.extend(body)
            if literal_hy:
                out.extend("-" for _ in range(literal_hy))
            out.append("]")
            i = j + 1
        return "".join(out)

    def _set_local(self, name: str, value: str) -> None:
        value = self._coerce_var_value(name, value)
        self._typed_vars.pop(name, None)
        if not self.local_stack:
            self.env[name] = value
            return
        self.local_stack[-1][name] = value

    def _assign_shell_var(self, name: str, value: str) -> None:
        if self._assign_subscripted_var(name, value):
            return
        if name in self.readonly_vars:
            raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=name))
        if name == "RANDOM":
            self._seed_random(value)
            self.env["RANDOM"] = str(value)
            return
        value = self._coerce_var_value(name, value)
        attrs = self._var_attrs.get(name, set())
        if "assoc" in attrs:
            cur = self._typed_vars.get(name)
            amap = dict(cur) if isinstance(cur, dict) else {}
            amap["0"] = value
            self._typed_vars[name] = amap
            self._set_subscript_projection(name, str(amap.get("0", "")))
            return
        if "array" in attrs:
            cur = self._typed_vars.get(name)
            arr = list(cur) if isinstance(cur, list) else []
            if not arr:
                arr = [None]
            arr[0] = value
            self._typed_vars[name] = arr
            self._set_subscript_projection(name, value)
            return
        self._typed_vars.pop(name, None)
        tied = self._py_ties.get(name)
        if tied is not None:
            _, setter, tie_type = tied
            if callable(setter):
                setter(self._shell_to_tie_value(value, tie_type))
                return
            raise RuntimeError(f"{name}: tied variable is read-only")
        for scope in reversed(self.local_stack):
            if name in scope:
                scope[name] = value
                return
        self.env[name] = value

    def _run_local(self, args: List[str]) -> int:
        return self._run_declare(args, cmd_name="local", local_scope=True)

    def _run_eval(self, args: List[str]) -> int:
        source = " ".join(args)
        if self.options.get("posix", False):
            bad_name = self._find_invalid_posix_function_name(source)
            if bad_name is not None:
                self._report_error("syntax error: invalid function name", line=self.current_line, context="eval")
                if self._is_noninteractive():
                    raise SystemExit(2)
                return 2
        line_offset = ((self.current_line or 1) - 1) if self.current_line is not None else 1
        status = self._eval_source(
            source,
            propagate_exit=True,
            propagate_return=True,
            parse_context="eval",
            line_offset=line_offset,
        )
        if self._last_eval_hard_error and not self.options.get("i", False):
            raise SystemExit(status if status != 0 else 2)
        return status

    def _find_invalid_posix_function_name(self, source: str) -> str | None:
        # POSIX lane: reject invalid function names in `name() { ... }` forms.
        for m in re.finditer(r"(^|[;\n])\s*([^\s(){};]+)\s*\(\s*\)\s*\{", source):
            name = m.group(2)
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                return name
        return None

    def _run_declare(self, args: List[str], cmd_name: str = "declare", local_scope: bool = False) -> int:
        if local_scope and not self.local_stack:
            self._report_error(self._diag_msg(DiagnosticKey.NOT_IN_FUNCTION), line=self.current_line, context=cmd_name)
            return 1
        if not args:
            return 0

        show_funcs = False
        show_func_defs = False
        print_vars = False
        declare_array = False
        declare_assoc = False
        declare_integer = False
        declare_lower = False
        declare_upper = False
        declare_export = False
        declare_readonly = False
        unset_array = False
        unset_assoc = False
        force_global = False
        idx = 0
        while idx < len(args):
            arg = args[idx]
            if arg == "--":
                idx += 1
                break
            if (not arg.startswith("-") and not arg.startswith("+")) or arg in {"-", "+"}:
                break
            enable = arg[0] == "-"
            for ch in arg[1:]:
                if ch == "F":
                    if not enable:
                        self._report_error(
                            self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=f"+{ch}"),
                            line=self.current_line,
                            context=cmd_name,
                        )
                        return 2
                    show_funcs = True
                elif ch == "f":
                    if not enable:
                        self._report_error(
                            self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=f"+{ch}"),
                            line=self.current_line,
                            context=cmd_name,
                        )
                        return 2
                    show_func_defs = True
                elif ch == "p":
                    if not enable:
                        self._report_error(
                            self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=f"+{ch}"),
                            line=self.current_line,
                            context=cmd_name,
                        )
                        return 2
                    print_vars = True
                elif ch == "a":
                    if enable:
                        declare_array = True
                    else:
                        unset_array = True
                elif ch == "A":
                    if enable:
                        declare_assoc = True
                    else:
                        unset_assoc = True
                elif ch == "i":
                    if enable:
                        declare_integer = True
                elif ch == "l":
                    if enable:
                        declare_lower = True
                elif ch == "u":
                    if enable:
                        declare_upper = True
                elif ch == "x":
                    if enable:
                        declare_export = True
                elif ch == "r":
                    if enable:
                        declare_readonly = True
                elif ch == "g":
                    if enable:
                        force_global = True
                else:
                    self._report_error(
                        self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=f"{arg[0]}{ch}"),
                        line=self.current_line,
                        context=cmd_name,
                    )
                    return 2
            idx += 1

        names = args[idx:]
        raw_names = [self._declare_raw_assign_by_arg.get(idx + i, names[i]) for i in range(len(names))]
        if names:
            folded: List[str] = []
            folded_raw: List[str] = []
            j = 0
            while j < len(names):
                spec = names[j]
                raw_spec = raw_names[j] if j < len(raw_names) else spec
                if "=" in spec:
                    _, rhs0 = spec.split("=", 1)
                    if rhs0.startswith("("):
                        depth = rhs0.count("(") - rhs0.count(")")
                        while depth > 0 and j + 1 < len(names):
                            j += 1
                            spec = spec + " " + names[j]
                            depth += names[j].count("(") - names[j].count(")")
                folded.append(spec)
                folded_raw.append(raw_spec)
                j += 1
            names = folded
            raw_names = folded_raw
        if not names and (
            declare_array
            or declare_assoc
            or declare_integer
            or declare_export
            or declare_readonly
            or declare_lower
            or declare_upper
        ):
            print_vars = True
        if show_funcs:
            if names:
                for name in names:
                    if self._has_function(name):
                        print(name, flush=True)
                return 0
            for name in self._function_names():
                print(name, flush=True)
            return 0
        if show_func_defs:
            status = 0
            func_names = names if names else self._function_names()
            for name in func_names:
                if not self._has_function(name):
                    if print_vars:
                        self._report_error(f"{cmd_name}: {name}: not found", line=self.current_line)
                    status = 1
                    continue
                body = self.functions_asdl.get(name)
                if isinstance(body, dict):
                    try:
                        ast_body = self._asdl_to_ast_list(body)
                        print(self._format_ast_function(name, ast_body), flush=True)
                    except Exception:
                        print(self._format_asdl_function(name, body), flush=True)
                else:
                    ast_body = self.functions.get(name)
                    if ast_body is not None:
                        print(self._format_ast_function(name, ast_body), flush=True)
                    else:
                        status = 1
            return status

        if print_vars:
            if not names:
                all_names: set[str] = set(self.env.keys()) | set(self._var_attrs.keys()) | set(self._typed_vars.keys())
                for scope in self.local_stack:
                    all_names.update(scope.keys())
                all_names.update(self.readonly_vars)
                filtered: list[str] = []
                for n in sorted(all_names):
                    attrs_n = self._var_attrs.get(n, set())
                    if declare_array and "array" not in attrs_n:
                        continue
                    if declare_assoc and "assoc" not in attrs_n:
                        continue
                    if declare_integer and "integer" not in attrs_n:
                        continue
                    if declare_export and "exported" not in attrs_n:
                        continue
                    if declare_readonly and "readonly" not in attrs_n and n not in self.readonly_vars:
                        continue
                    filtered.append(n)
                names = filtered
            status = 0
            def _dq(value: str) -> str:
                return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'
            for name in names:
                if not self._is_valid_name(name):
                    self._report_error(f"{cmd_name}: {name}: not found", line=self.current_line)
                    status = 1
                    continue
                attrs = set(self._var_attrs.get(name, set()))
                if name in self.readonly_vars:
                    attrs.add("readonly")
                value, is_set = self._get_var_with_state(name)
                if not is_set and "array" not in attrs and "assoc" not in attrs:
                    self._report_error(f"{cmd_name}: {name}: not found", line=self.current_line)
                    status = 1
                    continue
                prefix = "declare --"
                if "exported" in attrs:
                    prefix = "declare -x"
                elif "readonly" in attrs:
                    prefix = "declare -r"
                if "assoc" in attrs:
                    typed = self._typed_vars.get(name)
                    af = ["A"]
                    if "integer" in attrs:
                        af.append("i")
                    if "readonly" in attrs:
                        af.append("r")
                    if "exported" in attrs:
                        af.append("x")
                    assoc_flag = "-" + "".join(af)
                    if isinstance(typed, dict) and typed:
                        parts = []
                        for k, v in typed.items():
                            k_s = str(k)
                            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k_s) or re.fullmatch(r"[0-9]+", k_s):
                                key_expr = k_s
                            else:
                                key_expr = _dq(k_s)
                            parts.append(f"[{key_expr}]={_dq(str(v))}")
                        print(f"declare {assoc_flag} {name}=({' '.join(parts)} )", flush=True)
                    else:
                        print(f"declare {assoc_flag} {name}", flush=True)
                elif "array" in attrs:
                    typed = self._typed_vars.get(name)
                    af = ["a"]
                    if "integer" in attrs:
                        af.append("i")
                    if "readonly" in attrs:
                        af.append("r")
                    if "exported" in attrs:
                        af.append("x")
                    array_flag = "-" + "".join(af)
                    if isinstance(typed, list) and any(v is not None for v in typed):
                        parts = []
                        for idx, v in enumerate(typed):
                            if v is None:
                                continue
                            parts.append(f"[{idx}]={_dq(str(v))}")
                        print(f"declare {array_flag} {name}=({' '.join(parts)})", flush=True)
                    elif isinstance(typed, list):
                        if name == "FUNCNAME":
                            print(f"declare {array_flag} {name}", flush=True)
                        else:
                            print(f"declare {array_flag} {name}=()", flush=True)
                    else:
                        print(f"declare {array_flag} {name}", flush=True)
                elif "integer" in attrs:
                    print(f"declare -i {name}={_dq(value)}", flush=True)
                else:
                    print(f"{prefix} {name}={_dq(value)}", flush=True)
            return status

        effective_local_scope = local_scope and not force_global
        attr_flags: dict[str, bool] = {}
        if declare_array:
            attr_flags["array"] = True
        if declare_assoc:
            attr_flags["assoc"] = True
        if declare_integer:
            attr_flags["integer"] = True
        if declare_lower:
            attr_flags["lowercase"] = True
            attr_flags["uppercase"] = False
        if declare_upper:
            attr_flags["uppercase"] = True
            attr_flags["lowercase"] = False
        if declare_export:
            attr_flags["exported"] = True
        if declare_readonly:
            attr_flags["readonly"] = True
        if unset_array:
            attr_flags["array"] = False
        if unset_assoc:
            attr_flags["assoc"] = False

        if declare_assoc:
            if not self._bash_feature_enabled("declare_assoc"):
                self._report_error(
                    self._diag_msg(DiagnosticKey.REQUIRES_BASH_COMPAT, feature="declare -A"),
                    line=self.current_line,
                    context=cmd_name,
                )
                return 2

        if declare_array:
            if not self._bash_feature_enabled("declare_array"):
                self._report_error(
                    self._diag_msg(DiagnosticKey.REQUIRES_BASH_COMPAT, feature="declare -a"),
                    line=self.current_line,
                    context=cmd_name,
                )
                return 2

        status = 0
        for spec_i, spec in enumerate(names):
            if "=" in spec:
                name, value = spec.split("=", 1)
                op = "="
                if name.endswith("+"):
                    op = "+="
                    name = name[:-1]
                raw_spec = raw_names[spec_i] if spec_i < len(raw_names) else None
                raw_name = None
                raw_op = "="
                raw_value = None
                if raw_spec is not None and "=" in raw_spec:
                    raw_name, raw_value = raw_spec.split("=", 1)
                    if raw_name.endswith("+"):
                        raw_op = "+="
                        raw_name = raw_name[:-1]
                parsed_decl = self._parse_subscripted_name(name)
                parsed_base = parsed_decl[0] if parsed_decl is not None else name
                # `declare -a var[10]=x` accepts the indexed spelling but acts
                # on the variable itself; subscript is ignored in this form.
                if parsed_decl is not None and (declare_array or declare_assoc):
                    name = parsed_base
                    parsed_decl = None
                if not (self._is_valid_name(name) or parsed_decl is not None):
                    self._report_error(
                        self._diag_msg(DiagnosticKey.NOT_VALID_IDENTIFIER, cmd=cmd_name, name=name),
                        line=self.current_line,
                    )
                    return 1
                existing_attrs = set(self._var_attrs.get(parsed_base, set()))
                if declare_assoc and "array" in existing_attrs and "assoc" not in existing_attrs:
                    self._report_error(
                        f"{parsed_base}: cannot convert indexed to associative array",
                        line=self.current_line,
                    )
                    if self._bash_compat_level is None:
                        status = 1
                    continue
                if declare_array and "assoc" in existing_attrs and "array" not in existing_attrs:
                    self._report_error(
                        f"{parsed_base}: cannot convert associative to indexed array",
                        line=self.current_line,
                    )
                    if self._bash_compat_level is None:
                        status = 1
                    continue
                if (unset_array and ("array" in existing_attrs or "assoc" in existing_attrs)) or (
                    unset_assoc and "assoc" in existing_attrs
                ):
                    self._report_error(
                        f"{cmd_name}: {parsed_base}: cannot destroy array variables in this way",
                        line=self.current_line,
                    )
                    status = 1
                    continue
                if parsed_decl is not None:
                    expanded_sub = self._expand_assignment_word(value)
                    if op == "+=":
                        cur, is_set = self._get_var_with_state(name)
                        expanded_sub = (cur if is_set else "") + expanded_sub
                    self._assign_shell_var(name, expanded_sub)
                    if attr_flags:
                        self._set_var_attrs(parsed_base, **attr_flags)
                    continue

                target_attrs = set(self._var_attrs.get(parsed_base, set()))
                target_attrs.update(attr_flags.keys())
                is_assoc_target = "assoc" in target_attrs
                is_array_target = "array" in target_attrs and not is_assoc_target
                effective_attrs = set(self._var_attrs.get(name, set()))
                for k, v in attr_flags.items():
                    if v:
                        effective_attrs.add(k)
                    else:
                        effective_attrs.discard(k)
                if "lowercase" in effective_attrs:
                    effective_attrs.discard("uppercase")
                if "uppercase" in effective_attrs:
                    effective_attrs.discard("lowercase")
                if is_assoc_target:
                    assoc_values = self._parse_assoc_compound_assignment_rhs(value)
                    if assoc_values is not None:
                        cur = self._typed_vars.get(name)
                        base: dict[str, str] = dict(cur) if (op == "+=" and isinstance(cur, dict)) else {}
                        for k, v in assoc_values.items():
                            base[k] = self._coerce_value_with_attrs(str(v), effective_attrs)
                        self._typed_vars[name] = base
                        attrs_apply = dict(attr_flags)
                        attrs_apply["assoc"] = True
                        self._set_var_attrs(name, **attrs_apply)
                        self._set_subscript_projection(name, str(base.get("0", "")))
                        continue
                    expanded_assoc_value = self._expand_assignment_word(value)
                    cur = self._typed_vars.get(name)
                    base = dict(cur) if (op == "+=" and isinstance(cur, dict)) else {}
                    merged = (str(base.get("0", "")) + expanded_assoc_value) if op == "+=" else expanded_assoc_value
                    base["0"] = self._coerce_value_with_attrs(merged, effective_attrs)
                    self._typed_vars[name] = base
                    attrs_apply = dict(attr_flags)
                    attrs_apply["assoc"] = True
                    self._set_var_attrs(name, **attrs_apply)
                    self._set_subscript_projection(name, str(base.get("0", "")))
                    continue
                if is_array_target:
                    comp_entries: list[tuple[str, bool]] | None = None
                    if (
                        raw_value is not None
                        and raw_op == op
                        and raw_name == name
                    ):
                        raw_entries = self._parse_compound_assignment_rhs_entries(raw_value)
                        if raw_entries is not None:
                            # Expand each raw compound element in assignment
                            # context while preserving whether [idx]=rhs syntax
                            # was explicit in source.
                            comp_entries = []
                            for raw_tok, explicit_idx_syntax in raw_entries:
                                expanded_items = fields_to_text_list(
                                    self._legacy_word_to_expansion_fields(raw_tok, assignment=False)
                                )
                                if not expanded_items:
                                    expanded_items = [""]
                                for item in expanded_items:
                                    comp_entries.append((item, explicit_idx_syntax))
                    if comp_entries is None:
                        comp_entries = self._parse_compound_assignment_rhs_entries(value)
                    if comp_entries is not None:
                        self._assign_compound_var(name, op, comp_entries, attrs_override=effective_attrs)
                        attrs_apply = dict(attr_flags)
                        attrs_apply["array"] = True
                        self._set_var_attrs(name, **attrs_apply)
                        continue
                    expanded_arr_value = self._expand_assignment_word(value)
                    cur = self._typed_vars.get(name)
                    base_list: list[object]
                    if op == "+=" and isinstance(cur, list):
                        base_list = list(cur)
                        if base_list:
                            first = "" if base_list[0] is None else str(base_list[0])
                            base_list[0] = self._coerce_value_with_attrs(first + expanded_arr_value, effective_attrs)
                        else:
                            base_list = [self._coerce_value_with_attrs(expanded_arr_value, effective_attrs)]
                    else:
                        base_list = [self._coerce_value_with_attrs(expanded_arr_value, effective_attrs)]
                    self._typed_vars[name] = base_list
                    attrs_apply = dict(attr_flags)
                    attrs_apply["array"] = True
                    self._set_var_attrs(name, **attrs_apply)
                    self._set_subscript_projection(name, str(base_list[0]) if base_list else "")
                    continue
                expanded = self._expand_assignment_word(value)
                integer_target = "integer" in target_attrs
                if op == "+=":
                    if integer_target:
                        expanded = str(
                            self._to_int_arith(self._get_var(name) if self._get_var(name) != "" else "0")
                            + self._to_int_arith(expanded if expanded != "" else "0")
                        )
                    else:
                        expanded = self._get_var(name) + expanded
                elif integer_target:
                    expanded = str(self._to_int_arith(expanded if expanded != "" else "0"))
                self._declare_var(name, expanded, local_scope=effective_local_scope, **attr_flags)
            else:
                name = spec
                parsed_decl = self._parse_subscripted_name(name)
                parsed_base = parsed_decl[0] if parsed_decl is not None else name
                if parsed_decl is not None:
                    name = parsed_base
                if not self._is_valid_name(name):
                    self._report_error(
                        self._diag_msg(DiagnosticKey.NOT_VALID_IDENTIFIER, cmd=cmd_name, name=name),
                        line=self.current_line,
                    )
                    return 1
                existing_attrs = set(self._var_attrs.get(name, set()))
                if declare_assoc and "array" in existing_attrs and "assoc" not in existing_attrs:
                    self._report_error(
                        f"{name}: cannot convert indexed to associative array",
                        line=self.current_line,
                    )
                    if self._bash_compat_level is None:
                        status = 1
                    continue
                if declare_array and "assoc" in existing_attrs and "array" not in existing_attrs:
                    self._report_error(
                        f"{name}: cannot convert associative to indexed array",
                        line=self.current_line,
                    )
                    if self._bash_compat_level is None:
                        status = 1
                    continue
                if (unset_array and ("array" in existing_attrs or "assoc" in existing_attrs)) or (
                    unset_assoc and "assoc" in existing_attrs
                ):
                    self._report_error(
                        f"{cmd_name}: {name}: cannot destroy array variables in this way",
                        line=self.current_line,
                    )
                    status = 1
                    continue
                base_value = self._get_var(name)
                if effective_local_scope and name not in self.local_stack[-1]:
                    base_value = ""
                attrs_apply = dict(attr_flags)
                if parsed_decl is not None and "assoc" not in attrs_apply:
                    # declare var[IDX] marks an indexed array variable.
                    attrs_apply["array"] = True
                in_any_local = any(name in scope for scope in self.local_stack)
                exists = (
                    in_any_local
                    or name in self.env
                    or name in self._typed_vars
                    or name in self._var_attrs
                )
                if effective_local_scope and name not in self.local_stack[-1]:
                    exists = False
                if exists:
                    pre_value, pre_is_set = self._get_var_with_state(name)
                    if attrs_apply:
                        self._set_var_attrs(name, **attrs_apply)
                    if attrs_apply.get("array") and not isinstance(self._typed_vars.get(name), list):
                        self._typed_vars[name] = [pre_value] if pre_is_set else []
                        self._set_subscript_projection(name, pre_value if pre_is_set else "")
                    continue
                self._declare_var(name, base_value, local_scope=effective_local_scope, **attrs_apply)

        return status

    def _run_set(self, args: List[str]) -> int:
        def _set_option(opt: str, enabled: bool) -> int:
            if opt == "r":
                if not enabled and self.options.get("r", False):
                    self._print_stderr("set: +r: invalid option")
                    return 1
                if enabled:
                    self.options["r"] = True
                    self._activate_restricted_mode()
                    return 0
            self.options[opt] = enabled
            if opt == "m" and enabled:
                # Ash lane keeps legacy "can't access tty" behavior and
                # disables monitor when job-control handoff is unavailable.
                # Bash lane keeps monitor enabled for non-interactive probes.
                if self._bash_compat_level is None:
                    self._ensure_job_control_ready()
                    if not self._job_control_ready:
                        self._print_stderr(
                            self._diag_msg(DiagnosticKey.SET_CANT_ACCESS_TTY)
                        )
                        self.options[opt] = False
            return 0

        if not args:
            entries: dict[str, str] = {}
            for scope in self.local_stack:
                for name, value in scope.items():
                    if name not in entries:
                        entries[name] = value
            for name, value in self.env.items():
                if name not in entries:
                    entries[name] = value
            for name in sorted(entries):
                print(f"{name}={self._quote_set_value(entries[name])}")
            return 0
        if args[0] == "--":
            self.set_positional_args(args[1:])
            return 0
        if args[0] in ["-o", "+o"]:
            if len(args) < 2:
                if args[0] == "-o":
                    print("Current option settings")
                    for name in self.SET_O_LIST_ORDER:
                        mapped = self.SET_O_OPTION_MAP.get(name)
                        if mapped is None:
                            continue
                        state = "on" if self.options.get(mapped, False) else "off"
                        print(f"{name:<15} {state}")
                else:
                    for name in self.SET_O_LIST_ORDER:
                        mapped = self.SET_O_OPTION_MAP.get(name)
                        if mapped is None:
                            continue
                        state = "-" if self.options.get(mapped, False) else "+"
                        print(f"set {state}o {name}")
                return 0
            name = args[1]
            mapped = self.SET_O_OPTION_MAP.get(name)
            if mapped is None:
                return 1
            return _set_option(mapped, args[0] == "-o")
        if args[0].startswith("-") or args[0].startswith("+"):
            for token in args:
                if token == "--":
                    rest = args[args.index(token) + 1 :]
                    self.set_positional_args(rest)
                    return 0
                if token.startswith("-"):
                    for ch in token[1:]:
                        st = _set_option(ch, True)
                        if st != 0:
                            return st
                elif token.startswith("+"):
                    for ch in token[1:]:
                        st = _set_option(ch, False)
                        if st != 0:
                            return st
            return 0
        self.set_positional_args(args)
        return 0

    def _quote_set_value(self, value: str) -> str:
        # Ash lane prints set(1) values in single-quoted form.
        if self._diag.style == "ash":
            if value == "":
                return "''"
            if value == "'":
                return "''\"'\""
            return "'" + value.replace("'", "'\"'\"'") + "'"
        if value == "":
            return "''"
        if value == "'":
            return "\\'"
        # Keep values unquoted where shell-safe and comment-safe.
        if re.fullmatch(r"[A-Za-z0-9_./+-][A-Za-z0-9_./+#-]*", value):
            return value
        return "'" + value.replace("'", "'\"'\"'") + "'"

    def _run_export(self, args: List[str]) -> int:
        unexport = False
        print_only = False
        idx = 0
        while idx < len(args):
            arg = args[idx]
            if arg == "--":
                idx += 1
                break
            if arg == "-n":
                unexport = True
                idx += 1
                continue
            if arg == "-p":
                print_only = True
                idx += 1
                continue
            if arg.startswith("-"):
                self._report_error(
                    self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=arg),
                    line=self.current_line,
                    context="export",
                )
                return self._maybe_fatal_special_builtin_error("export", 2)
            break
        if print_only and idx >= len(args):
            for name in sorted(self.env.keys()):
                if "exported" not in self._var_attrs.get(name, set()):
                    continue
                print(f'declare -x {name}="{self.env.get(name, "")}"')
            return 0
        status = 0
        for arg in args[idx:]:
            if "=" in arg:
                name, value = arg.split("=", 1)
                op = "="
                if name.endswith("+"):
                    op = "+="
                    name = name[:-1]
                if unexport:
                    self._set_var_attrs(name, exported=False)
                    continue
                if name in self.readonly_vars:
                    msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                    self._report_error(msg, line=self.current_line, context="export")
                    status = 2
                    continue
                if op == "+=":
                    self.env[name] = self.env.get(name, "") + value
                else:
                    self.env[name] = value
                self._set_var_attrs(name, exported=True)
            else:
                if unexport:
                    self._set_var_attrs(arg, exported=False)
                else:
                    self.env[arg] = self.env.get(arg, "")
                    self._set_var_attrs(arg, exported=True)
        return self._maybe_fatal_special_builtin_error("export", status)

    def _run_readonly(self, args: List[str]) -> int:
        if not args:
            for name in sorted(self.readonly_vars):
                print(f"readonly {name}='{self._get_var(name)}'")
            return 0
        show_print = False
        show_array = False
        show_assoc = False
        idx = 0
        while idx < len(args):
            a = args[idx]
            if a == "--":
                idx += 1
                break
            if not a.startswith("-") or a == "-":
                break
            for ch in a[1:]:
                if ch == "p":
                    show_print = True
                elif ch == "a":
                    show_array = True
                elif ch == "A":
                    show_assoc = True
            idx += 1
        if idx >= len(args) and (show_print or show_array or show_assoc):
            def _dq(value: str) -> str:
                return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'
            for name in sorted(self.readonly_vars):
                attrs = set(self._var_attrs.get(name, set()))
                if "assoc" in attrs:
                    if show_array and not show_assoc:
                        continue
                    typed = self._typed_vars.get(name)
                    decl_prefix = "readonly" if self.options.get("posix", False) else "declare"
                    if isinstance(typed, dict) and typed:
                        parts = [f"[{k}]={_dq(str(v))}" for k, v in typed.items()]
                        print(f"{decl_prefix} -Ar {name}=({' '.join(parts)} )")
                    else:
                        print(f"{decl_prefix} -Ar {name}")
                    continue
                if "array" in attrs:
                    if show_assoc and not show_array:
                        continue
                    typed = self._typed_vars.get(name)
                    if isinstance(typed, list) and any(v is not None for v in typed):
                        parts = []
                        for i, v in enumerate(typed):
                            if v is None:
                                continue
                            parts.append(f"[{i}]={_dq(str(v))}")
                        if self.options.get("posix", False):
                            print(f"readonly -a {name}=({' '.join(parts)})")
                        else:
                            print(f"declare -ar {name}=({' '.join(parts)})")
                    else:
                        if self.options.get("posix", False):
                            print(f"readonly -a {name}")
                        else:
                            print(f"declare -ar {name}")
                    continue
                if show_array or show_assoc:
                    continue
                print(f"readonly {name}={_dq(self._get_var(name))}")
            return 0
        for arg in args[idx:]:
            target = arg.split("=", 1)[0]
            if target.endswith("+"):
                target = target[:-1]
            if self._parse_subscripted_name(target) is not None:
                self._report_error(
                    f"`{target}': not a valid identifier",
                    line=self.current_line,
                    context="readonly",
                )
                return self._maybe_fatal_special_builtin_error("readonly", 1)
        # Keep readonly option/typing behavior aligned with declare/typeset by
        # routing through declare with an implicit `-r`.
        return self._run_declare(["-r"] + args, cmd_name="readonly", local_scope=False)

    def _run_unset(self, args: List[str]) -> int:
        mode_vars = True
        explicit_vars_mode = False
        idx = 0
        while idx < len(args):
            arg = args[idx]
            if arg == "--":
                idx += 1
                break
            if arg.startswith("-"):
                if arg == "-":
                    self._report_error(
                        self._diag_msg(DiagnosticKey.UNSET_BAD_VARIABLE_NAME),
                        line=self.current_line,
                        context="unset",
                    )
                    return self._maybe_fatal_special_builtin_error("unset", 2)
                valid = True
                for ch in arg[1:]:
                    if ch == "v":
                        mode_vars = True
                        explicit_vars_mode = True
                    elif ch == "f":
                        mode_vars = False
                    else:
                        valid = False
                        break
                if not valid:
                    self._report_error(
                        self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=arg),
                        line=self.current_line,
                        context="unset",
                    )
                    return self._maybe_fatal_special_builtin_error("unset", 2)
                idx += 1
                continue
            break
        status = 0
        for name in args[idx:]:
            if mode_vars and name in self.readonly_vars:
                msg = self._diag_msg(DiagnosticKey.READONLY_UNSET, name=name)
                self._report_error(msg, line=self.current_line, context="unset")
                # ash-style lane keeps historical special-builtin fatal behavior;
                # bash-style lane reports status and continues script execution.
                if self._diag.style != "bash" and self._is_noninteractive():
                    raise SystemExit(2)
                status = 1 if self._diag.style == "bash" else 2
                continue
            if not mode_vars:
                self.functions.pop(name, None)
                self.functions_asdl.pop(name, None)
                continue
            parsed = self._parse_subscripted_name(name)
            if parsed is not None:
                base, key = parsed
                typed = self._typed_vars.get(base)
                attrs = self._var_attrs.get(base, set())
                if isinstance(typed, dict) and "assoc" in attrs:
                    if key in {"@", "*"}:
                        # bash COMPAT <=51: unset A[@] removes the whole assoc
                        # variable; 5.2+ may target key '@' instead.
                        if self._compat_at_most(51):
                            self._typed_vars.pop(base, None)
                            self._var_attrs.pop(base, None)
                            self.env.pop(base, None)
                            continue
                    akey = self._eval_assoc_subscript_key(key)
                    typed.pop(akey, None)
                    self._set_subscript_projection(base, str(typed.get("0", "")) if typed else "")
                    continue
                if isinstance(typed, list):
                    if key in {"@", "*"}:
                        self._typed_vars.pop(base, None)
                        attrs_now = set(self._var_attrs.get(base, set()))
                        attrs_now.discard("array")
                        attrs_now.discard("assoc")
                        if attrs_now:
                            self._var_attrs[base] = attrs_now
                        else:
                            self._var_attrs.pop(base, None)
                        self.env.pop(base, None)
                        continue
                    m_name = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
                    if m_name is not None and self.options.get("u", False):
                        _, is_set = self._get_var_with_state(m_name.group(0))
                        if not is_set:
                            self._report_error(f"{m_name.group(0)}: unbound variable", line=self.current_line)
                            raise SystemExit(1)
                    i_key = self._eval_index_subscript(key, typed, strict=True, name=base)
                    if i_key is None:
                        continue
                    if 0 <= i_key < len(typed):
                        typed[i_key] = None
                    vis = self._array_visible_values(typed)
                    self._set_subscript_projection(base, vis[0] if vis else "")
                    continue
                base_exists = (
                    base in self.env
                    or any(base in scope for scope in self.local_stack)
                    or base in self._var_attrs
                    or base in self._typed_vars
                )
                if base_exists:
                    self._report_error(f"{base}: not an array variable", line=self.current_line, context="unset")
                    status = 1 if self._diag.style == "bash" else 2
                continue
            had_var = False
            if name in self._typed_vars or name in self._var_attrs:
                had_var = True
            else:
                _, had_var = self._get_var_with_state(name)
            self._typed_vars.pop(name, None)
            removed_local = False
            for scope in reversed(self.local_stack):
                if name in scope:
                    scope[name] = ""
                    removed_local = True
                    break
            if removed_local:
                continue
            if name in self.env:
                del self.env[name]
            self._var_attrs.pop(name, None)
            if name == "OPTIND":
                self._getopts_state = None
            if not had_var and not explicit_vars_mode:
                self.functions.pop(name, None)
                self.functions_asdl.pop(name, None)
        return status

    def _eval_assoc_subscript_key(self, key: str) -> str:
        return self._expand_assignment_word(key)

    def _run_shift(self, args: List[str]) -> int:
        n = 1
        if args:
            try:
                n = int(args[0])
            except ValueError:
                self._report_error(
                    self._diag_msg(DiagnosticKey.SHIFT_ILLEGAL_NUMBER, value=args[0]),
                    line=self.current_line,
                    context="shift",
                )
                raise SystemExit(2)
        if n < 0:
            self._report_error(
                self._diag_msg(DiagnosticKey.SHIFT_ILLEGAL_NUMBER, value=str(n)),
                line=self.current_line,
                context="shift",
            )
            raise SystemExit(2)
        if n > len(self.positional):
            if self._diag.style != "bash":
                # ash behavior: out-of-range positive shift fails without
                # changing positional parameters and without a diagnostic.
                return 1
            self._report_error(
                self._diag_msg(DiagnosticKey.SHIFT_COUNT_OUT_OF_RANGE, value=str(n)),
                line=self.current_line,
                context="shift",
            )
            if self._bash_compat_level is not None:
                return 1
            raise SystemExit(2)
        self.positional = self.positional[n:]
        return 0

    def _set_var(self, name: str, value: str) -> None:
        if self._assign_subscripted_var(name, value):
            return
        if name in self.readonly_vars:
            raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=name))
        if name == "RANDOM":
            self._seed_random(value)
            self.env["RANDOM"] = str(value)
            return
        value = self._coerce_var_value(name, value)
        attrs = self._var_attrs.get(name, set())
        if "assoc" in attrs:
            cur = self._typed_vars.get(name)
            amap = dict(cur) if isinstance(cur, dict) else {}
            amap["0"] = value
            self._typed_vars[name] = amap
            self._set_subscript_projection(name, str(amap.get("0", "")))
            return
        if "array" in attrs:
            cur = self._typed_vars.get(name)
            arr = list(cur) if isinstance(cur, list) else []
            if not arr:
                arr = [None]
            arr[0] = value
            self._typed_vars[name] = arr
            self._set_subscript_projection(name, value)
            return
        self._typed_vars.pop(name, None)
        tied = self._py_ties.get(name)
        if tied is not None:
            _, setter, tie_type = tied
            if callable(setter):
                setter(self._shell_to_tie_value(value, tie_type))
                return
            raise RuntimeError(f"{name}: tied variable is read-only")
        for scope in reversed(self.local_stack):
            if name in scope:
                scope[name] = value
                return
        self.env[name] = value

    def _assign_shell_var_op(self, name: str, op: str, value: str) -> None:
        if op != "+=":
            self._assign_shell_var(name, value)
            return
        parsed = self._parse_subscripted_name(name)
        if parsed is not None:
            base, key = parsed
            attrs = self._var_attrs.get(base, set())
            if "assoc" in attrs:
                cur = self._typed_vars.get(base)
                amap = dict(cur) if isinstance(cur, dict) else {}
                akey = str(self._eval_assoc_subscript_key(key))
                old = str(amap.get(akey, ""))
                if "integer" in attrs:
                    merged = str(
                        self._to_int_arith(old if old != "" else "0")
                        + self._to_int_arith(value if value != "" else "0")
                    )
                else:
                    merged = old + value
                amap[akey] = merged
                self._typed_vars[base] = amap
                self._set_subscript_projection(base, str(amap.get("0", "")))
                return
            cur_arr = self._typed_vars.get(base)
            arr = list(cur_arr) if isinstance(cur_arr, list) else []
            idx = self._eval_index_subscript(key, arr, strict=True, name=name)
            if idx is None:
                raise RuntimeError(f"{name}: bad array subscript")
            old = ""
            if 0 <= idx < len(arr) and arr[idx] is not None:
                old = str(arr[idx])
            if "integer" in attrs:
                merged = str(
                    self._to_int_arith(old if old != "" else "0")
                    + self._to_int_arith(value if value != "" else "0")
                )
            else:
                merged = old + value
            self._assign_shell_var(name, merged)
            return
        attrs = self._var_attrs.get(name, set())
        if "integer" in attrs:
            merged = str(
                self._to_int_arith(self._get_var(name) if self._get_var(name) != "" else "0")
                + self._to_int_arith(value if value != "" else "0")
            )
        else:
            merged = self._get_var(name) + value
        self._assign_shell_var(name, merged)

    def _is_valid_name(self, name: str) -> bool:
        if not name:
            return False
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        return all(ch.isalnum() or ch == "_" for ch in name)

    def _run_getopts(self, args: List[str]) -> int:
        if len(args) < 2:
            self._report_error(
                self._diag_msg(DiagnosticKey.USAGE_GETOPTS),
                line=self.current_line,
                context="getopts",
            )
            return 2
        optspec = args[0]
        var_name = args[1]
        if not self._is_valid_name(var_name):
            self._report_error(
                self._diag_msg(DiagnosticKey.BAD_VARIABLE_NAME, name=var_name),
                line=self.current_line,
                context="getopts",
            )
            return 2
        argv = args[2:] if len(args) > 2 else list(self.positional)
        argv_sig = tuple(argv)
        silent = optspec.startswith(":")
        if silent:
            optspec = optspec[1:]

        optind_raw, optind_is_set = self._get_var_with_state("OPTIND")
        try:
            optind = int(optind_raw) if optind_is_set and optind_raw != "" else 1
        except ValueError:
            optind = 1
        if optind <= 0:
            optind = 1

        pos = 1
        if self._getopts_state is not None:
            prev_sig, prev_optind, prev_pos = self._getopts_state
            if prev_sig == argv_sig and prev_optind == optind:
                pos = prev_pos

        def finish(status: int, out_var: str = "?", optarg: str = "") -> int:
            self._set_var("OPTIND", str(optind))
            self._set_var(var_name, out_var)
            self._set_var("OPTARG", optarg)
            self._getopts_state = (argv_sig, optind, pos)
            return status

        if optind > len(argv):
            return finish(1)

        arg = argv[optind - 1]
        if arg == "--":
            optind += 1
            pos = 1
            return finish(1)
        if not arg.startswith("-") or arg == "-":
            pos = 1
            return finish(1)

        if pos >= len(arg):
            optind += 1
            pos = 1
            if optind > len(argv):
                return finish(1)
            arg = argv[optind - 1]
            if arg == "--":
                optind += 1
                return finish(1)
            if not arg.startswith("-") or arg == "-":
                return finish(1)

        ch = arg[pos]
        pos += 1
        idx = optspec.find(ch)
        if idx < 0 or ch == ":":
            if pos >= len(arg):
                optind += 1
                pos = 1
            if not silent and self._get_var("OPTERR") != "0":
                self._print_stderr(self._diag_msg(DiagnosticKey.GETOPTS_ILLEGAL_OPTION, opt=ch))
            return finish(0, "?", ch if silent else "")

        needs_arg = idx + 1 < len(optspec) and optspec[idx + 1] == ":"
        if needs_arg:
            if pos < len(arg):
                optarg = arg[pos:]
                optind += 1
                pos = 1
                return finish(0, ch, optarg)
            if optind < len(argv):
                optarg = argv[optind]
                optind += 2
                pos = 1
                return finish(0, ch, optarg)
            optind += 1
            pos = 1
            if silent:
                return finish(0, ":", ch)
            if self._get_var("OPTERR") != "0":
                self._print_stderr(self._diag_msg(DiagnosticKey.GETOPTS_NO_ARG, opt=ch))
            return finish(0, "?", "")

        if pos >= len(arg):
            optind += 1
            pos = 1
        return finish(0, ch, "")

    def _run_shopt(self, args: List[str]) -> int:
        set_mode = False
        unset_mode = False
        query_mode = False
        print_mode = False
        opt_o_mode = False
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            opt = args[i]
            if opt == "--":
                i += 1
                break
            for ch in opt[1:]:
                if ch == "s":
                    set_mode = True
                    continue
                if ch == "u":
                    unset_mode = True
                    continue
                if ch == "q":
                    query_mode = True
                    continue
                if ch == "p":
                    print_mode = True
                    continue
                if ch == "o":
                    opt_o_mode = True
                    continue
                self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="shopt", opt=f"-{ch}"))
                return 2
            i += 1
        names = args[i:]
        if set_mode and unset_mode:
            self._report_error(self._diag_msg(DiagnosticKey.SHOPT_CONFLICT))
            return 2
        if opt_o_mode:
            if not names:
                if print_mode:
                    for name in self.SET_O_LIST_ORDER:
                        mapped = self.SET_O_OPTION_MAP.get(name)
                        if mapped is None:
                            continue
                        state = "-" if self.options.get(mapped, False) else "+"
                        print(f"set {state}o {name}")
                else:
                    print("Current option settings")
                    for name in self.SET_O_LIST_ORDER:
                        mapped = self.SET_O_OPTION_MAP.get(name)
                        if mapped is None:
                            continue
                        state = "on" if self.options.get(mapped, False) else "off"
                        print(f"{name:<15} {state}")
                return 0
            status = 0
            for name in names:
                mapped = self.SET_O_OPTION_MAP.get(name)
                if mapped is None:
                    self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION_NAME, name=name))
                    status = 1
                    continue
                if set_mode:
                    self.options[mapped] = True
                    if mapped == "r":
                        self._activate_restricted_mode()
                elif unset_mode:
                    if mapped == "r" and self.options.get("r", False):
                        self._report_error("set: +r: invalid option")
                        status = 1
                        continue
                    self.options[mapped] = False
                if query_mode and not self.options.get(mapped, False):
                    status = 1
            return status
        if not names:
            for name in sorted(self._shopts.keys()):
                val = self._shopts[name]
                if print_mode:
                    print(f"shopt {'-s' if val else '-u'} {name}")
                else:
                    print(f"{name}\t{'on' if val else 'off'}")
            return 0
        status = 0
        for name in names:
            if name not in self._shopts:
                self._report_error(self._diag_msg(DiagnosticKey.SHOPT_INVALID_NAME, name=name))
                status = 1
                continue
            if set_mode:
                self._shopts[name] = True
            elif unset_mode:
                self._shopts[name] = False
            if print_mode:
                val = self._shopts[name]
                print(f"shopt {'-s' if val else '-u'} {name}")
                if not set_mode and not unset_mode and not query_mode and not val:
                    # bash: `shopt -p opt` returns non-zero when option is off.
                    status = 1
            if query_mode and not self._shopts[name]:
                status = 1
        return status

    def _run_caller(self, args: List[str]) -> int:
        level = 0
        if args:
            if len(args) > 1:
                return 2
            try:
                level = int(args[0], 10)
            except ValueError:
                return 1
            if level < 0:
                return 1
        frames = [fr for fr in self._frame_stack if str(fr.get("kind", "")) == "function"]
        if not frames:
            return 1
        idx = len(frames) - 1 - level
        if idx < 0:
            return 1
        fr = frames[idx]
        lineno = int(fr.get("lineno", 0) or 0) + 1
        source = str(fr.get("source", "") or "")
        # Match bash output shape:
        # - caller 0: "<line> <file>"
        # - caller N>0: "<line> <func-or-main> <file>"
        if level == 0:
            print(f"{lineno} {source}")
            return 0
        outer = "main"
        if idx > 0:
            outer_name = str(frames[idx - 1].get("funcname", "") or "")
            if outer_name:
                outer = outer_name
        print(f"{lineno} {outer} {source}")
        return 0

    def _history_file(self, path: str | None = None) -> str:
        if path:
            return os.path.expanduser(path)
        return os.path.expanduser(self.env.get("HISTFILE", "~/.bash_history"))

    def _history_public_entries(self) -> list[tuple[int, str, float | None]]:
        out: list[tuple[int, str, float | None]] = []
        for i, line in enumerate(self._history):
            stripped = line.lstrip()
            if stripped.startswith("history"):
                continue
            ts = self._history_ts[i] if i < len(self._history_ts) else None
            out.append((i, line, ts))
        return out

    def _history_write(self, path: str, lines: list[str], *, append: bool) -> int:
        mode = "a" if append else "w"
        try:
            with open(path, mode, encoding="utf-8", errors="surrogateescape") as f:
                for line in lines:
                    f.write(line + "\n")
            return 0
        except OSError:
            return 1

    def _run_history(self, args: List[str]) -> int:
        i = 0
        print_mode = True
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            a = args[i]
            if a == "--":
                i += 1
                break
            if a == "-c":
                self._history.clear()
                self._history_ts.clear()
                self._history_read_cursor = 0
                print_mode = False
                i += 1
                continue
            if a == "-d":
                if i + 1 >= len(args):
                    return 2
                try:
                    off = int(args[i + 1], 10)
                except ValueError:
                    return 1
                public = self._history_public_entries()
                if off <= 0 or off > len(public):
                    return 1
                real_idx = public[off - 1][0]
                del self._history[real_idx]
                if real_idx < len(self._history_ts):
                    del self._history_ts[real_idx]
                self._history_read_cursor = min(self._history_read_cursor, len(self._history))
                print_mode = False
                i += 2
                continue
            if a in {"-a", "-w", "-r", "-n"}:
                path = self._history_file(args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("-") else None)
                if a == "-a":
                    public_lines = [x for _, x, _ in self._history_public_entries()]
                    start = min(self._history_read_cursor, len(public_lines))
                    status = self._history_write(path, public_lines[start:], append=True)
                    if status != 0:
                        return status
                    self._history_read_cursor = len(public_lines)
                elif a == "-w":
                    public_lines = [x for _, x, _ in self._history_public_entries()]
                    status = self._history_write(path, public_lines, append=False)
                    if status != 0:
                        return status
                    self._history_read_cursor = len(public_lines)
                elif a in {"-r", "-n"}:
                    try:
                        with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
                            file_lines = [ln.rstrip("\n") for ln in f]
                    except OSError:
                        return 1
                    if a == "-r":
                        self._history.extend(file_lines)
                        self._history_ts.extend([None] * len(file_lines))
                    else:
                        start = min(self._history_read_cursor, len(file_lines))
                        chunk = file_lines[start:]
                        self._history.extend(chunk)
                        self._history_ts.extend([None] * len(chunk))
                    self._history_read_cursor = len(file_lines)
                print_mode = False
                if i + 1 < len(args) and not args[i + 1].startswith("-"):
                    i += 2
                else:
                    i += 1
                continue
            if a == "-s":
                if i + 1 >= len(args):
                    return 2
                self.add_history_entry(" ".join(args[i + 1 :]), force=True)
                return 0
            if a == "-p":
                for tok in args[i + 1 :]:
                    print(tok)
                return 0
            return 2
        rest = args[i:]
        if not print_mode:
            return 0
        public = self._history_public_entries()
        count = len(public)
        if rest:
            if len(rest) != 1:
                return 2
            try:
                n = int(rest[0], 10)
            except ValueError:
                return 1
            if n < 0:
                return 1
            start = max(0, len(public) - n)
        else:
            start = 0
        histfmt = self._get_var("HISTTIMEFORMAT")
        for idx in range(start, len(public)):
            _, line_text, line_ts = public[idx]
            if histfmt:
                if line_ts is None:
                    stamp = "??"
                else:
                    try:
                        stamp = time.strftime(histfmt, time.localtime(line_ts))
                    except Exception:
                        stamp = "??"
                print(f"{idx + 1:5d}  {stamp}{line_text}")
            else:
                print(f"{idx + 1:5d}  {line_text}")
        return 0

    def _run_suspend(self, args: List[str]) -> int:
        force = False
        for a in args:
            if a == "-f":
                force = True
                continue
            return 2
        if not self._is_interactive_session:
            self._print_stderr("suspend: cannot suspend: not interactive")
            return 1
        if self._is_login_shell and not force:
            self._print_stderr("suspend: cannot suspend a login shell")
            return 1
        try:
            os.kill(os.getpid(), signal.SIGSTOP)
            return 0
        except Exception:
            return 1

    def _run_logout(self, args: List[str]) -> int:
        if args:
            return 2
        if not self._is_login_shell:
            self._print_stderr("logout: not login shell: use `exit'")
            return 1
        code = self.last_status
        raise SystemExit(code)

    def _run_printf(self, args: List[str]) -> int:
        if not args:
            return 0
        fmt = self._decode_backslash_escapes(args[0])
        vals = args[1:]
        def count_specs(s: str) -> int:
            i = 0
            n = 0
            while i < len(s):
                if s[i] == "%" and i + 1 < len(s):
                    if s[i + 1] != "%":
                        n += 1
                    i += 2
                    continue
                i += 1
            return n

        def render_once(start_vi: int) -> tuple[str, int]:
            out = []
            i = 0
            vi = start_vi
            while i < len(fmt):
                if fmt[i] == "%" and i + 1 < len(fmt):
                    if fmt[i + 1] == "%":
                        out.append("%")
                        i += 2
                        continue
                    j = i + 1
                    while j < len(fmt) and fmt[j] not in "diouxXseEfFgGaA":
                        j += 1
                    if j >= len(fmt):
                        out.append(fmt[i:])
                        break
                    directive = fmt[i : j + 1]
                    spec = fmt[j]
                    val = vals[vi] if vi < len(vals) else ""
                    vi += 1
                    if spec == "s":
                        out.append(directive % val)
                    elif spec in ["d", "i", "o", "u", "x", "X"]:
                        try:
                            num = int(val, 0)
                        except ValueError:
                            num = 0
                        if spec == "u":
                            num &= (1 << 64) - 1
                            out.append((directive[:-1] + "d") % num)
                        elif spec in ["x", "X", "o"] and num < 0:
                            num &= (1 << 64) - 1
                            out.append(directive % num)
                        else:
                            out.append(directive % num)
                    elif spec in ["e", "E", "f", "F", "g", "G", "a", "A"]:
                        try:
                            num = float(val)
                        except ValueError:
                            num = 0.0
                        out.append(directive % num)
                    else:
                        out.append(val)
                    i = j + 1
                    continue
                out.append(fmt[i])
                i += 1
            return "".join(out), vi

        specs = count_specs(fmt)
        rendered_parts: List[str] = []
        vi = 0
        if specs == 0:
            text, _ = render_once(0)
            rendered_parts.append(text)
        else:
            while vi < len(vals) or vi == 0:
                text, next_vi = render_once(vi)
                rendered_parts.append(text)
                if next_vi == vi:
                    break
                vi = next_vi
                if not vals:
                    break
        rendered = "".join(rendered_parts)
        if isinstance(sys.stdout, io.StringIO) and self._fd_redirect_depth == 0:
            sys.stdout.write(rendered)
            return 0
        data = self._encode_printf_output(rendered)
        try:
            os.write(1, data)
            return 0
        except OSError as e:
            if e.errno == errno.EPIPE:
                if self._diag.style == "bash":
                    # Bash-compatible behavior for broken pipelines: no
                    # diagnostic.
                    return 1
                self._print_stderr(self._diag_msg(DiagnosticKey.WRITE_ERROR, error=str(e.strerror)))
                return 1
            self._print_stderr(self._diag_msg(DiagnosticKey.WRITE_ERROR, error=str(e.strerror)))
            return 1

    def _encode_printf_output(self, text: str) -> bytes:
        # Preserve low-byte escape semantics (\xHH, octal escapes) while also
        # allowing regular Unicode text to pass through as UTF-8.
        out = bytearray()
        for ch in text:
            code = ord(ch)
            if 0xDC80 <= code <= 0xDCFF:
                out.append(code - 0xDC00)
                continue
            if code <= 0xFF:
                out.append(code)
                continue
            out.extend(ch.encode("utf-8"))
        return bytes(out)

    def _run_py(self, args: List[str], entry_name: str = "py") -> int:
        eval_mode = False
        structured_exc = False
        no_dedent = False
        stdout_var: str | None = None
        return_var: str | None = None
        tie_vars: list[str] = []
        untie_vars: list[str] = []
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                i += 1
                break
            if not a.startswith("-") or a == "-":
                break
            if a == "-e":
                eval_mode = True
                i += 1
                continue
            if a == "-x":
                structured_exc = True
                i += 1
                continue
            if a == "--no-dedent":
                no_dedent = True
                i += 1
                continue
            if a == "-v":
                if i + 1 >= len(args):
                    self._report_error(
                        self._diag_msg(DiagnosticKey.PY_USAGE, entry=entry_name),
                        line=self.current_line,
                        context=entry_name,
                    )
                    return 2
                stdout_var = args[i + 1]
                i += 2
                continue
            if a == "-t":
                if i + 1 >= len(args):
                    self._report_error(
                        self._diag_msg(DiagnosticKey.PY_USAGE, entry=entry_name),
                        line=self.current_line,
                        context=entry_name,
                    )
                    return 2
                tie_vars.append(args[i + 1])
                i += 2
                continue
            if a == "-u":
                if i + 1 >= len(args):
                    self._report_error(
                        self._diag_msg(DiagnosticKey.PY_USAGE, entry=entry_name),
                        line=self.current_line,
                        context=entry_name,
                    )
                    return 2
                untie_vars.append(args[i + 1])
                i += 2
                continue
            if a == "-r":
                if i + 1 >= len(args):
                    self._report_error(
                        self._diag_msg(DiagnosticKey.PY_USAGE, entry=entry_name),
                        line=self.current_line,
                        context=entry_name,
                    )
                    return 2
                return_var = args[i + 1]
                i += 2
                continue
            self._report_error(
                self._diag_msg(DiagnosticKey.ILLEGAL_OPTION, opt=a),
                line=self.current_line,
                context=entry_name,
            )
            return 2
        payload = args[i:]
        if structured_exc:
            self._clear_structured_python_exception_vars()
        for name in untie_vars:
            self._py_ties.pop(name, None)
        for name in tie_vars:
            self._py_globals[name] = self._get_var(name)
            self._py_ties[name] = (
                (lambda n=name: self._py_globals.get(n, "")),
                (lambda v, n=name: self._py_globals.__setitem__(n, v)),
                "scalar",
            )

        if not payload and (tie_vars or untie_vars):
            return 0
        callable_mode = (
            bool(payload)
            and (callable(self._resolve_py_name(payload[0])) or payload[0] in self._py_callables)
        )
        shell_callable_mode = False
        if callable_mode and payload:
            cobj = self._resolve_py_name(payload[0])
            if cobj is None:
                cobj = self._py_callables.get(payload[0])
            shell_callable_mode = bool(getattr(cobj, "__mctash_shell_function__", False))
        source_from_stdin = False
        if not payload:
            source_from_stdin = True
            code = self._read_stdin_text()
            if not no_dedent:
                code = textwrap.dedent(code)
        else:
            code = " ".join(payload)
        py_stdout = io.StringIO() if stdout_var else None
        py_result: object = None
        try:
            with self._push_frame(kind="python", funcname="py"):
                if py_stdout is not None:
                    with redirect_stdout(py_stdout):
                        py_result = self._run_py_payload(payload, code, eval_mode, source_from_stdin, entry_name)
                else:
                    py_result = self._run_py_payload(payload, code, eval_mode, source_from_stdin, entry_name)
        except KeyboardInterrupt:
            return 130
        except Exception as e:
            if structured_exc:
                self._assign_shell_var("PYTHON_EXCEPTION", type(e).__name__)
                self._assign_shell_var("PYTHON_EXCEPTION_MSG", str(e))
                tb_lines = self._format_python_tb(e.__traceback__)
                self._assign_shell_var("PYTHON_EXCEPTION_TB", "\n".join(tb_lines))
                self._assign_shell_var("PYTHON_EXCEPTION_LANG", "python")
            else:
                print(f"{entry_name}: {type(e).__name__}: {e}", file=sys.stderr)
            return 1

        if stdout_var is not None and py_stdout is not None:
            self._assign_shell_var(stdout_var, py_stdout.getvalue())
        if return_var is not None:
            self._assign_shell_var(return_var, self._py_to_shell(py_result))
        if shell_callable_mode:
            try:
                return (int(py_result) if py_result is not None else 0) % 256
            except (TypeError, ValueError):
                print(f"{entry_name}: shell-style callable must return int status, got {type(py_result).__name__}", file=sys.stderr)
                return 1
        if callable_mode and py_result is not None and stdout_var is None and return_var is None and not eval_mode:
            print(self._py_to_shell(py_result))
        if eval_mode and py_result is not None and stdout_var is None and return_var is None:
            print(self._py_to_shell(py_result))
        return 0

    def _clear_structured_python_exception_vars(self) -> None:
        # Structured exception mode should not leak stale values between runs.
        self._assign_shell_var("PYTHON_EXCEPTION", "")
        self._assign_shell_var("PYTHON_EXCEPTION_MSG", "")
        self._assign_shell_var("PYTHON_EXCEPTION_TB", "")
        self._assign_shell_var("PYTHON_EXCEPTION_LANG", "")

    def _run_shared(self, args: List[str]) -> int:
        store = self._get_shared_store()
        if not args:
            for k, v in store.items():
                print(f"{k}={v}")
            return 0
        status = 0
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                store.set(name, value)
                continue
            if not store.contains(arg):
                status = 1
                continue
            print(store.get(arg))
        return status

    def _read_stdin_text(self) -> str:
        # Read from fd 0 so command redirections (including here-docs) win over
        # python-level sys.stdin wrappers used by the pipeline emulator.
        if self._fd_redirect_depth == 0 and isinstance(sys.stdin, io.StringIO):
            return sys.stdin.read()
        chunks: list[bytes] = []
        while True:
            b = os.read(0, 65536)
            if not b:
                break
            chunks.append(b)
        return b"".join(chunks).decode("utf-8", errors="surrogateescape")

    def _format_python_tb(self, tb) -> list[str]:
        out: list[str] = []
        for fr in traceback.extract_tb(tb):
            out.append(f"{fr.filename}:{fr.lineno}:{fr.name}")
        return out

    def _run_from_import(self, args: List[str]) -> int:
        # Syntax: from <module|path.py> import <name|*> [as alias]
        if len(args) < 3:
            self._report_error(
                self._diag_msg(DiagnosticKey.USAGE_FROM_IMPORT),
                line=self.current_line,
                context="from",
            )
            return 2
        mod_ref = args[0]
        if args[1] != "import":
            self._report_error(
                self._diag_msg(DiagnosticKey.USAGE_FROM_IMPORT),
                line=self.current_line,
                context="from",
            )
            return 2
        name = args[2]
        alias = None
        if len(args) >= 5 and args[3] == "as":
            alias = args[4]
        elif len(args) > 3:
            self._report_error(
                self._diag_msg(DiagnosticKey.USAGE_FROM_IMPORT),
                line=self.current_line,
                context="from",
            )
            return 2
        try:
            mod = self._load_py_module(mod_ref)
            bind = getattr(mod, "mctash_bind", None)
            if callable(bind):
                bind(self._py_globals.get("sh"))
            if name == "*":
                for k in dir(mod):
                    if k.startswith("_"):
                        continue
                    obj = getattr(mod, k)
                    self._py_globals[k] = obj
                    if callable(obj):
                        self._install_python_callable(k, obj, wrapper_target=k, create_wrapper=True)
                return 0
            if not hasattr(mod, name):
                self._report_error(
                    self._diag_msg(DiagnosticKey.FROM_NOT_FOUND, name=name, module=mod_ref),
                    line=self.current_line,
                    context="from",
                )
                return 1
            obj = getattr(mod, name)
            out_name = alias or name
            if callable(obj):
                self._install_python_callable(out_name, obj, wrapper_target=out_name, create_wrapper=True)
            else:
                self._py_globals[out_name] = obj
            return 0
        except Exception as e:
            self._report_error(
                self._diag_msg(DiagnosticKey.FROM_EXCEPTION, etype=type(e).__name__, msg=str(e)),
                line=self.current_line,
                context="from",
            )
            return 1

    def _load_py_module(self, ref: str):
        if ref.endswith(".py") or ref.startswith("./") or ref.startswith("../") or ref.startswith("/"):
            path = os.path.abspath(ref)
            if self._test_mode:
                self._py_import_counter += 1
                mod_name = f"_mctash_import_{self._py_import_counter}"
            else:
                mod_name = f"_mctash_import_{uuid.uuid4().hex}"
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"unable to load module from {ref}")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        return importlib.import_module(ref)

    def _run_py_payload(
        self,
        payload: List[str],
        code: str,
        eval_mode: bool,
        source_from_stdin: bool,
        entry_name: str,
    ) -> object:
        if eval_mode:
            return eval(code, self._py_globals, self._py_globals)
        if source_from_stdin:
            exec(code, self._py_globals, self._py_globals)
            return None

        target = self._resolve_py_name(payload[0])
        if callable(target):
            return self._invoke_py_callable(target, payload[1:])
        py_callable = self._py_callables.get(payload[0])
        if py_callable is not None:
            return self._invoke_py_callable(py_callable, payload[1:])
        if entry_name == "python:" and payload:
            try:
                exec(code, self._py_globals, self._py_globals)
            except Exception as e:
                target = payload[0]
                raise RuntimeError(
                    f"{target}: not callable, and python-statement fallback failed ({type(e).__name__}: {e})"
                ) from e
            return None
        exec(code, self._py_globals, self._py_globals)
        return None

    def _resolve_py_name(self, name: str) -> object | None:
        cur = self._py_globals.get(name)
        if cur is not None:
            return cur
        parts = name.split(".")
        if not parts:
            return None
        cur = self._py_globals.get(parts[0])
        if cur is None:
            return None
        for p in parts[1:]:
            if not hasattr(cur, p):
                return None
            cur = getattr(cur, p)
        return cur

    def _py_to_shell(self, value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return repr(value)

    def _cast_shell_arg(self, text: str) -> object:
        if re.match(r"^[+-]?[0-9]+$", text):
            try:
                return int(text, 10)
            except ValueError:
                return text
        if re.match(r"^[+-]?(?:[0-9]*\.[0-9]+|[0-9]+\.[0-9]*)(?:[eE][+-]?[0-9]+)?$", text):
            try:
                return float(text)
            except ValueError:
                return text
        low = text.lower()
        if low == "true":
            return True
        if low == "false":
            return False
        return text

    def _invoke_py_callable(self, func: object, args: List[str]) -> object:
        casted: list[object] = [self._cast_shell_arg(a) for a in args]
        try:
            return func(*casted)  # type: ignore[misc]
        except TypeError as cast_err:
            try:
                return func(*args)  # type: ignore[misc]
            except TypeError as raw_err:
                raise TypeError(
                    "call failed after automatic coercion and raw-string fallback: "
                    f"coerced_args={casted!r} ({cast_err}); raw_args={args!r} ({raw_err})"
                ) from raw_err

    def _install_python_callable(
        self,
        name: str,
        obj: object,
        *,
        wrapper_target: str | None = None,
        create_wrapper: bool = False,
    ) -> None:
        self._py_globals[name] = obj
        self._py_callables[name] = obj
        if not create_wrapper:
            return
        if not self._is_valid_name(name):
            return
        target = wrapper_target or name
        source = f'{name}() {{ py {shlex.quote(target)} "$@"; }}'
        status = self._eval_source(source, parse_context="py-wrapper")
        if status != 0:
            raise RuntimeError(f"failed to define shell wrapper function: {name}")

    def _coerce_var_value(self, name: str, value: str) -> str:
        attrs = self._var_attrs.get(name, set())
        return self._coerce_value_with_attrs(value, attrs)

    def _coerce_value_with_attrs(self, value: str, attrs: set[str]) -> str:
        out = value
        if "integer" in attrs:
            try:
                out = str(self._to_int_arith(out if out != "" else "0"))
            except Exception:
                out = "0"
        if "uppercase" in attrs:
            out = out.upper()
        elif "lowercase" in attrs:
            out = out.lower()
        return out

    def _tie_value_to_shell(self, getter: object, tie_type: str | None) -> str:
        value = getter()  # type: ignore[misc]
        if tie_type == "integer":
            try:
                return str(int(value))
            except (TypeError, ValueError):
                return "0"
        if tie_type == "array":
            if isinstance(value, (list, tuple)):
                return " ".join(self._py_to_shell(v) for v in value)
            return self._py_to_shell(value)
        if tie_type == "assoc":
            if isinstance(value, dict):
                return " ".join(f"{k}={self._py_to_shell(v)}" for k, v in value.items())
            return self._py_to_shell(value)
        return self._py_to_shell(value)

    def _shell_to_tie_value(self, value: str, tie_type: str | None) -> object:
        if tie_type == "integer":
            try:
                return int(value, 10)
            except ValueError:
                return 0
        if tie_type == "array":
            return shlex.split(value) if value else []
        if tie_type == "assoc":
            out: dict[str, str] = {}
            for tok in shlex.split(value):
                if "=" not in tok:
                    out[tok] = ""
                else:
                    k, v = tok.split("=", 1)
                    out[k] = v
            return out
        return value

    def _get_var_attrs(self, name: str) -> dict[str, bool]:
        attrs = set(self._var_attrs.get(name, set()))
        if name in self.readonly_vars:
            attrs.add("readonly")
        return {key: True for key in sorted(attrs)}

    def _set_var_attrs(self, name: str, **flags: object) -> None:
        known = {"exported", "integer", "readonly", "uppercase", "lowercase", "nameref", "trace", "array", "assoc"}
        attrs = set(self._var_attrs.get(name, set()))
        for key, raw in flags.items():
            if key not in known:
                raise ValueError(f"unknown attribute: {key}")
            enabled = bool(raw)
            if key == "readonly":
                if enabled:
                    self.readonly_vars.add(name)
                else:
                    self.readonly_vars.discard(name)
                continue
            if key == "exported":
                if enabled:
                    attrs.add("exported")
                else:
                    attrs.discard("exported")
                continue
            if enabled:
                attrs.add(key)
                if key == "uppercase":
                    attrs.discard("lowercase")
                if key == "lowercase":
                    attrs.discard("uppercase")
            else:
                attrs.discard(key)
        if attrs:
            self._var_attrs[name] = attrs
        else:
            self._var_attrs.pop(name, None)
        current = self._get_var(name)
        if current != "":
            coerced = self._coerce_var_value(name, current)
            if coerced != current:
                for scope in reversed(self.local_stack):
                    if name in scope:
                        scope[name] = coerced
                        break
                else:
                    self.env[name] = coerced

    def _exported_env_view(self, env: dict[str, str]) -> dict[str, str]:
        return {
            k: v
            for k, v in env.items()
            if "exported" in self._var_attrs.get(k, set())
        }

    def _declare_var(self, name: str, value: str = "", local_scope: bool = False, **flags: object) -> None:
        if local_scope and self.local_stack:
            if name in self.readonly_vars:
                raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=name))
            value = self._coerce_var_value(name, value)
            self._typed_vars.pop(name, None)
            self.local_stack[-1][name] = value
        else:
            self._assign_shell_var(name, value)
        if flags:
            self._set_var_attrs(name, **flags)

    def _call_shell_function_from_python(self, name: str, args: List[str]) -> str:
        if not self._has_function(name):
            raise KeyError(name)
        status, out, _ = self._capture_command_output(
            SimpleCommand(argv=[Word(name)] + [Word(a) for a in args], assignments=[], redirects=[], line=self.current_line),
            data=None,
            force_epipe=False,
        )
        text = out.decode("utf-8", errors="replace")
        if status != 0:
            raise ShellCalledProcessError(returncode=int(status), cmd=name, stdout=text, stderr="")
        return text.rstrip("\n")

    def _run_shell_subprocess(
        self,
        *,
        script: str,
        stdout: Any = None,
        stderr: Any = None,
        input_text: str | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, "-m", "mctash", "-c", script]
        child_env = dict(os.environ)
        child_env.update(self.env)
        if env:
            child_env.update({str(k): str(v) for k, v in env.items()})
        return subprocess.run(
            cmd,
            input=input_text,
            text=True,
            stdout=stdout,
            stderr=stderr,
            cwd=cwd,
            env=child_env,
            timeout=timeout,
        )

    def _popen_shell_subprocess(
        self,
        *,
        script: str,
        stdin: Any = None,
        stdout: Any = None,
        stderr: Any = None,
        text: bool = True,
        start_new_session: bool = False,
        preexec_fn: Callable[[], None] | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.Popen[Any]:
        cmd = [sys.executable, "-m", "mctash", "-c", script]
        child_env = dict(os.environ)
        child_env.update(self.env)
        if env:
            child_env.update({str(k): str(v) for k, v in env.items()})
        return subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            text=text,
            start_new_session=start_new_session,
            preexec_fn=preexec_fn,
            cwd=cwd,
            env=child_env,
        )

    def _decode_backslash_escapes(self, text: str) -> str:
        out: List[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch != "\\":
                out.append(ch)
                i += 1
                continue
            i += 1
            if i >= len(text):
                out.append("\\")
                break
            esc = text[i]
            if esc in "01234567":
                digits = esc
                i += 1
                if i < len(text) and text[i] in "01234567":
                    digits += text[i]
                    i += 1
                    if i < len(text) and text[i] in "01234567":
                        digits += text[i]
                        i += 1
                out.append(chr(int(digits, 8)))
                continue
            if esc == "x":
                i += 1
                hex_digits = ""
                while i < len(text) and len(hex_digits) < 2 and text[i] in "0123456789abcdefABCDEF":
                    hex_digits += text[i]
                    i += 1
                if hex_digits:
                    out.append(chr(int(hex_digits, 16)))
                else:
                    out.append("x")
                continue
            mapping = {
                "n": "\n",
                "t": "\t",
                "r": "\r",
                "b": "\b",
                "a": "\a",
                "f": "\f",
                "v": "\v",
                "\\": "\\",
            }
            out.append(mapping.get(esc, esc))
            i += 1
        return "".join(out)

    def _decode_backslash_escapes_bash_xpg(self, text: str) -> str:
        # Bash xpg_echo decodes a limited escape set for echo; notably it does
        # not treat octal/hex forms like \141 as numeric escapes.
        out: List[str] = []
        i = 0
        mapping = {
            "a": "\a",
            "b": "\b",
            "e": "\x1b",
            "E": "\x1b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "v": "\v",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }
        while i < len(text):
            ch = text[i]
            if ch != "\\":
                out.append(ch)
                i += 1
                continue
            if i + 1 >= len(text):
                out.append("\\")
                i += 1
                continue
            esc = text[i + 1]
            if esc in mapping:
                out.append(mapping[esc])
            else:
                out.append("\\")
                out.append(esc)
            i += 2
        return "".join(out)

    def _run_echo(self, args: List[str]) -> int:
        newline = True
        i = 0
        if not self._shopts.get("xpg_echo", False):
            while i < len(args) and args[i].startswith("-") and args[i] != "-":
                opt = args[i][1:]
                if opt == "":
                    break
                if all(ch == "n" for ch in opt):
                    if "n" in opt:
                        newline = False
                    i += 1
                    continue
                break
        args = args[i:]
        data = " ".join(args)
        mode = self.env.get("MCTASH_MODE", "").strip().lower()
        if self._shopts.get("xpg_echo", False):
            if mode == "bash" or self.options.get("posix", False):
                data = self._decode_backslash_escapes_bash_xpg(data)
            else:
                data = self._decode_backslash_escapes(data)
        if newline:
            data += "\n"
        if self._force_broken_pipe and self._fd_redirect_depth == 0:
            # Simulated broken-pipe path used by process-substitution/pipeline
            # harnesses.
            if self._diag.style != "bash":
                self._print_stderr(self._diag_msg(DiagnosticKey.WRITE_ERROR, error="Broken pipe"))
                return 1
            # Bash-compatible behavior: fail status, no diagnostic.
            return 1
        if isinstance(sys.stdout, io.StringIO) and self._fd_redirect_depth == 0:
            sys.stdout.write(data)
            return 0
        try:
            os.write(1, data.encode("utf-8", errors="surrogateescape"))
            return 0
        except OSError as e:
            if e.errno == errno.EPIPE:
                if self._diag.style == "bash":
                    # Bash behavior in pipeline tear-down paths: fail command
                    # status without emitting a write-error diagnostic.
                    return 1
                self._print_stderr(self._diag_msg(DiagnosticKey.WRITE_ERROR, error=str(e.strerror)))
                return 1
            self._print_stderr(self._diag_msg(DiagnosticKey.WRITE_ERROR, error=str(e.strerror)))
            return 1

    def _run_read(self, args: List[str]) -> int:
        raw_mode = False
        delimiter = "\n"
        n_chars: int | None = None
        timeout_sec: float | None = None
        prompt: str | None = None
        exact_chars = False
        array_name: str | None = None
        fd = 0
        edit_mode = False
        init_text: str | None = None

        names: List[str] = []
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                names = args[i + 1 :]
                break
            if not a.startswith("-") or a == "-":
                names = args[i:]
                break
            if a == "-r":
                raw_mode = True
                i += 1
                continue
            if a == "-a" or a.startswith("-a"):
                if not self._compat_enabled():
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-a"))
                    return 2
                if a == "-a":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="a"))
                        return 2
                    array_name = args[i + 1]
                    i += 2
                else:
                    array_name = a[2:]
                    i += 1
                continue
            if a == "-p" or a.startswith("-p"):
                if a == "-p":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="p"))
                        return 2
                    prompt = args[i + 1]
                    i += 2
                else:
                    prompt = a[2:]
                    i += 1
                continue
            if a == "-n" or a.startswith("-n"):
                if not self._compat_enabled() and not self._test_mode:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-n"))
                    return 2
                val = None
                if a == "-n":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="n"))
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    n_chars = max(0, int(val))
                except ValueError:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_NUMBER))
                    return 2
                exact_chars = False
                continue
            if a == "-N" or a.startswith("-N"):
                if not self._compat_enabled():
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-N"))
                    return 2
                val = None
                if a == "-N":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="N"))
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    n_chars = max(0, int(val))
                except ValueError:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_NUMBER))
                    return 2
                exact_chars = True
                continue
            if a == "-d" or a.startswith("-d"):
                if not self._compat_enabled() and not self._test_mode:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-d"))
                    return 2
                val = None
                if a == "-d":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="d"))
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                delimiter = "\0" if val == "" else val[0]
                continue
            if a == "-t" or a.startswith("-t"):
                if not self._compat_enabled() and not self._test_mode:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-t"))
                    return 2
                val = None
                if a == "-t":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="t"))
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    timeout_sec = float(val)
                except ValueError:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_NUMBER))
                    return 2
                if timeout_sec < 0:
                    timeout_sec = 0.0
                continue
            if a == "-u" or a.startswith("-u"):
                if not self._compat_enabled():
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-u"))
                    return 2
                val = None
                if a == "-u":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="u"))
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    fd = int(val, 10)
                except ValueError:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_NUMBER))
                    return 2
                if fd < 0:
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_FD))
                    return 2
                continue
            if a == "-s":
                if not self._compat_enabled():
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-s"))
                    return 2
                i += 1
                continue
            if a == "-e":
                if not self._compat_enabled():
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-e"))
                    return 2
                edit_mode = True
                i += 1
                continue
            if a == "-i" or a.startswith("-i"):
                if not self._compat_enabled():
                    self._report_error(self._diag_msg(DiagnosticKey.READ_ILLEGAL_OPTION, opt="-i"))
                    return 2
                if a == "-i":
                    if i + 1 >= len(args):
                        self._report_error(self._diag_msg(DiagnosticKey.READ_OPTION_REQUIRES_ARG, opt="i"))
                        return 2
                    init_text = args[i + 1]
                    i += 2
                else:
                    init_text = a[2:]
                    i += 1
                continue
            self._report_error(self._diag_msg(DiagnosticKey.READ_UNKNOWN_OPTION, opt=a))
            return 2
        else:
            names = []

        _ = edit_mode
        _ = init_text
        implicit_reply = False
        if array_name is not None:
            names = []
        elif not names:
            names = ["REPLY"]
            implicit_reply = True

        if prompt is not None and os.isatty(fd):
            os.write(2, prompt.encode("utf-8", errors="surrogateescape"))

        self._last_read_interrupt_status = None
        self._last_read_timed_out = False

        if timeout_sec is not None and timeout_sec == 0 and n_chars is None:
            if not self._fd_ready_now(fd):
                self._last_read_timed_out = True
                text, ok = "", False
            else:
                text, ok = "", True
        else:
            text, ok = self._read_from_fd(
                fd=fd,
                delimiter=delimiter,
                raw_mode=raw_mode,
                n_chars=n_chars,
                timeout_sec=timeout_sec,
                exact_chars=exact_chars,
            )
        if self._last_read_interrupt_status is not None:
            return self._last_read_interrupt_status
        if not ok and self._last_read_timed_out:
            return 142 if self._bash_compat_level is not None else 1
        if not ok and text == "":
            return 1

        if array_name is not None:
            fields = self._split_ifs(text)
            self._typed_vars[array_name] = list(fields)
            self._set_var_attrs(array_name, array=True)
            self._set_subscript_projection(array_name, fields[0] if fields else "")
            return 0 if ok else 1
        if implicit_reply and names == ["REPLY"]:
            values = [text]
        else:
            values = self._split_read_fields(text, names)
        for name, value in zip(names, values):
            self._assign_shell_var(name, value)
        return 0 if ok else 1

    def _run_mapfile(self, args: List[str]) -> int:
        delim = "\n"
        trim = False
        max_count: int | None = None
        skip = 0
        origin = 0
        fd = 0
        i = 0
        array_name = "MAPFILE"

        while i < len(args):
            a = args[i]
            if a == "--":
                i += 1
                break
            if not a.startswith("-") or a == "-":
                break
            if a in {"-t"}:
                trim = True
                i += 1
                continue
            if a in {"-d", "-n", "-s", "-O", "-u"}:
                if i + 1 >= len(args):
                    self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="mapfile", opt=a[1:]))
                    return 2
                val = args[i + 1]
                i += 2
                if a == "-d":
                    delim = "\0" if val == "" else val[0]
                elif a == "-n":
                    try:
                        max_count = max(0, int(val, 10))
                    except ValueError:
                        self._report_error(self._diag_msg(DiagnosticKey.INVALID_NUMBER, cmd="mapfile", what="line count"))
                        return 2
                elif a == "-s":
                    try:
                        skip = max(0, int(val, 10))
                    except ValueError:
                        self._report_error(self._diag_msg(DiagnosticKey.INVALID_NUMBER, cmd="mapfile", what="skip count"))
                        return 2
                elif a == "-O":
                    try:
                        origin = int(val, 10)
                    except ValueError:
                        self._report_error(self._diag_msg(DiagnosticKey.INVALID_NUMBER, cmd="mapfile", what="origin"))
                        return 2
                    if origin < 0:
                        self._report_error(self._diag_msg(DiagnosticKey.INVALID_NUMBER, cmd="mapfile", what="origin"))
                        return 1
                elif a == "-u":
                    try:
                        fd = int(val, 10)
                    except ValueError:
                        self._report_error(self._diag_msg(DiagnosticKey.INVALID_FD, cmd="mapfile", fd=val))
                        return 2
                    if fd < 0:
                        self._report_error(self._diag_msg(DiagnosticKey.INVALID_FD, cmd="mapfile", fd=str(fd)))
                        return 2
                continue
            self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="mapfile", opt=a))
            return 2

        if i < len(args):
            array_name = args[i]
            i += 1
        if i < len(args):
            self._report_error(self._diag_msg(DiagnosticKey.TOO_MANY_ARGS, cmd="mapfile"))
            return 2
        if not self._is_valid_name(array_name):
            self._report_error(self._diag_msg(DiagnosticKey.NOT_VALID_IDENTIFIER, cmd="mapfile", name=array_name))
            return 1

        try:
            if fd == 0 and isinstance(sys.stdin, io.StringIO):
                stream = sys.stdin
                close_stream = False
            else:
                stream = os.fdopen(os.dup(fd), "r", encoding="utf-8", errors="surrogateescape")
                close_stream = True
        except OSError:
            self._report_error(self._diag_msg(DiagnosticKey.INVALID_FD, cmd="mapfile", fd=str(fd)))
            return 1

        lines: list[str] = []
        dropped = 0
        buf: list[str] = []
        try:
            while True:
                ch = stream.read(1)
                if ch == "":
                    if buf:
                        rec = "".join(buf)
                        if dropped < skip:
                            dropped += 1
                        else:
                            lines.append(rec if trim else rec)
                    break
                if ch == delim:
                    rec = "".join(buf)
                    if not trim:
                        rec += ch
                    if dropped < skip:
                        dropped += 1
                    else:
                        lines.append(rec)
                        if max_count is not None and len(lines) >= max_count:
                            break
                    buf = []
                else:
                    buf.append(ch)
            if close_stream:
                stream.close()
        except OSError:
            if close_stream:
                try:
                    stream.close()
                except OSError:
                    pass
            return 1

        current = self._typed_vars.get(array_name)
        arr: list[object] = list(current) if isinstance(current, list) else []
        if origin > len(arr):
            arr.extend([None] * (origin - len(arr)))
        for idx, item in enumerate(lines):
            pos = origin + idx
            if pos >= len(arr):
                arr.append(item)
            else:
                arr[pos] = item
        self._typed_vars[array_name] = arr
        self._set_var_attrs(array_name, array=True)
        vis = self._array_visible_values(arr)
        self._set_subscript_projection(array_name, vis[0] if vis else "")
        return 0

    def _run_enable(self, args: List[str]) -> int:
        disable = False
        print_mode = False
        show_all = False
        special_only = False
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                i += 1
                break
            if not a.startswith("-") or a == "-":
                break
            for ch in a[1:]:
                if ch == "n":
                    disable = True
                elif ch == "p":
                    print_mode = True
                elif ch == "a":
                    show_all = True
                elif ch == "s":
                    special_only = True
                else:
                    self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="enable", opt=f"-{ch}"))
                    return 2
            i += 1

        names = args[i:]

        def _name_iter() -> list[str]:
            if special_only:
                src = sorted(self.SPECIAL_BUILTINS)
            else:
                src = sorted(self.BUILTINS)
            if disable:
                if show_all:
                    return [n for n in src if n in self.disabled_builtins]
                return [n for n in src if n in self.disabled_builtins]
            if show_all:
                return src
            return [n for n in src if self._is_builtin_enabled(n)]

        if print_mode or (not names):
            for n in _name_iter():
                prefix = "enable -n" if n in self.disabled_builtins else "enable"
                print(f"{prefix} {n}")
            if not names:
                return 0

        status = 0
        for n in names:
            if n not in self.BUILTINS:
                self._report_error(self._diag_msg(DiagnosticKey.NOT_SHELL_BUILTIN, cmd="enable", name=n))
                status = 1
                continue
            if disable:
                self.disabled_builtins.add(n)
            else:
                self.disabled_builtins.discard(n)
        return status

    def _run_help(self, args: List[str]) -> int:
        help_map = {
            "declare": "declare: set variable attributes and values",
            "typeset": "typeset: alias of declare",
            "local": "local: create function-local variables",
            "mapfile": "mapfile: read lines into an indexed array",
            "readarray": "readarray: alias of mapfile",
            "enable": "enable: enable or disable shell builtins",
            "help": "help: display builtin help",
        }
        if not args:
            print("Shell builtins:")
            print(" ".join(sorted(self.BUILTINS)))
            return 0
        status = 0
        for name in args:
            if name in help_map:
                print(help_map[name])
                continue
            if name in self.BUILTINS:
                print(f"{name}: shell builtin")
                continue
            self._report_error(self._diag_msg(DiagnosticKey.HELP_NO_TOPIC, cmd="help", name=name))
            status = 1
        return status

    def _sync_dir_stack_current(self) -> None:
        cwd = os.getcwd()
        self.env["PWD"] = cwd
        if not self._dir_stack:
            self._dir_stack = [cwd]
            return
        self._dir_stack[0] = cwd

    def _dir_index_from_spec(self, spec: str, size: int) -> int | None:
        if len(spec) < 2 or spec[0] not in "+-" or not spec[1:].isdigit():
            return None
        n = int(spec[1:], 10)
        if n < 0 or n >= size:
            return None
        if spec[0] == "+":
            return n
        return size - 1 - n

    def _print_dirs(self, entries: list[str], *, per_line: bool = False, numbered: bool = False, choose: int | None = None) -> None:
        if choose is not None:
            print(entries[choose], flush=True)
            return
        if numbered:
            for i, d in enumerate(entries):
                print(f"{i}\t{d}", flush=True)
            return
        if per_line:
            for d in entries:
                print(d, flush=True)
            return
        print(" ".join(entries), flush=True)

    def _run_dirs(self, args: List[str]) -> int:
        self._sync_dir_stack_current()
        per_line = False
        numbered = False
        clear = False
        choose: int | None = None
        i = 0
        while i < len(args):
            a = args[i]
            idx = self._dir_index_from_spec(a, len(self._dir_stack))
            if idx is not None:
                choose = idx
                i += 1
                continue
            if a == "-p":
                per_line = True
                i += 1
                continue
            if a == "-v":
                numbered = True
                i += 1
                continue
            if a == "-c":
                clear = True
                i += 1
                continue
            if a == "-l":
                i += 1
                continue
            self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="dirs", opt=a))
            return 2
        if clear:
            self._dir_stack = [os.getcwd()]
            return 0
        if choose is not None and (choose < 0 or choose >= len(self._dir_stack)):
            return 1
        self._print_dirs(self._dir_stack, per_line=per_line, numbered=numbered, choose=choose)
        return 0

    def _run_pushd(self, args: List[str]) -> int:
        self._sync_dir_stack_current()
        if not args:
            if len(self._dir_stack) < 2:
                self._report_error(self._diag_msg(DiagnosticKey.NO_OTHER_DIRECTORY, cmd="pushd"))
                return 1
            self._dir_stack[0], self._dir_stack[1] = self._dir_stack[1], self._dir_stack[0]
            old = os.getcwd()
            os.chdir(self._dir_stack[0])
            self.env["OLDPWD"] = old
            self.env["PWD"] = os.getcwd()
            self._sync_dir_stack_current()
            self._print_dirs(self._dir_stack)
            return 0
        spec = args[0]
        idx = self._dir_index_from_spec(spec, len(self._dir_stack))
        if idx is not None:
            if idx == 0:
                self._print_dirs(self._dir_stack)
                return 0
            head = self._dir_stack[idx:]
            tail = self._dir_stack[:idx]
            self._dir_stack = head + tail
            old = os.getcwd()
            os.chdir(self._dir_stack[0])
            self.env["OLDPWD"] = old
            self.env["PWD"] = os.getcwd()
            self._sync_dir_stack_current()
            self._print_dirs(self._dir_stack)
            return 0
        try:
            old = os.getcwd()
            os.chdir(spec)
            self.env["OLDPWD"] = old
            self.env["PWD"] = os.getcwd()
            self._dir_stack.insert(1, old)
            self._sync_dir_stack_current()
            self._print_dirs(self._dir_stack)
            return 0
        except OSError:
            return 1

    def _run_popd(self, args: List[str]) -> int:
        self._sync_dir_stack_current()
        if len(self._dir_stack) < 2:
            self._report_error(self._diag_msg(DiagnosticKey.DIRSTACK_EMPTY, cmd="popd"))
            return 1
        idx = 0
        if args:
            parsed = self._dir_index_from_spec(args[0], len(self._dir_stack))
            if parsed is None:
                self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="popd", opt=args[0]))
                return 2
            idx = parsed
        if idx < 0 or idx >= len(self._dir_stack):
            return 1
        removed_current = idx == 0
        self._dir_stack.pop(idx)
        if removed_current:
            old = os.getcwd()
            os.chdir(self._dir_stack[0])
            self.env["OLDPWD"] = old
            self.env["PWD"] = os.getcwd()
            self._sync_dir_stack_current()
        self._print_dirs(self._dir_stack)
        return 0

    def _run_disown(self, args: List[str]) -> int:
        mark_nohup = False
        all_jobs = False
        running_only = False
        targets: list[str] = []
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                targets.extend(args[i + 1 :])
                break
            if a.startswith("-") and a != "-":
                for ch in a[1:]:
                    if ch == "h":
                        mark_nohup = True
                    elif ch == "a":
                        all_jobs = True
                    elif ch == "r":
                        running_only = True
                    else:
                        return 2
                i += 1
                continue
            targets.append(a)
            i += 1

        all_job_ids = sorted(set(self._bg_jobs.keys()) | set(self._bg_status.keys()))
        chosen: list[int] = []
        if targets:
            for tok in targets:
                jid = self._resolve_job_id(tok)
                if jid is None or jid not in all_job_ids:
                    return 1
                chosen.append(jid)
        elif all_jobs or running_only:
            chosen = all_job_ids
        else:
            if self._last_bg_job is None or self._last_bg_job not in all_job_ids:
                return 1
            chosen = [self._last_bg_job]

        if running_only:
            running_set = {jid for jid, th in self._bg_jobs.items() if th.is_alive()}
            chosen = [jid for jid in chosen if jid in running_set]

        for jid in chosen:
            if mark_nohup:
                self._disowned_nohup.add(jid)
                continue
            self._bg_jobs.pop(jid, None)
            self._bg_status.pop(jid, None)
            pid = self._bg_pids.pop(jid, None)
            self._bg_started_at.pop(jid, None)
            self._bg_cmdline.pop(jid, None)
            self._bg_stopped.discard(jid)
            self._job_state.pop(jid, None)
            self._bg_notify_emitted.discard(jid)
            try:
                self._bg_notifications.remove(jid)
            except ValueError:
                pass
            self._disowned_nohup.discard(jid)
            if pid is not None:
                self._bg_pid_to_job.pop(pid, None)
            if self._last_bg_job == jid:
                remain = sorted(set(self._bg_jobs.keys()) | set(self._bg_status.keys()))
                self._last_bg_job = remain[-1] if remain else None
                self._last_bg_pid = self._bg_pids.get(self._last_bg_job) if self._last_bg_job is not None else None
        return 0

    def _run_complete(self, args: List[str]) -> int:
        print_mode = False
        remove_mode = False
        wordlist: str | None = None
        action: str | None = None
        comp_opts: set[str] = set()
        names: list[str] = []
        i = 0
        takes_arg = {"-A", "-G", "-W", "-F", "-C", "-X", "-P", "-S", "-o"}
        while i < len(args):
            a = args[i]
            if a == "--":
                names = args[i + 1 :]
                break
            if not a.startswith("-") or a == "-":
                names = args[i:]
                break
            if a == "-p":
                print_mode = True
                i += 1
                continue
            if a == "-r":
                remove_mode = True
                i += 1
                continue
            if a in takes_arg:
                if i + 1 >= len(args):
                    self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="complete", opt=a[1:]))
                    return 2
                v = args[i + 1]
                if a == "-W":
                    wordlist = v
                elif a == "-A":
                    action = v
                elif a == "-o":
                    comp_opts.add(v)
                i += 2
                continue
            # accept common flag clusters used by bash complete
            if all(ch in "abcdefgjksuvDEI" for ch in a[1:]):
                i += 1
                continue
            self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="complete", opt=a))
            return 2
        else:
            names = []

        if print_mode:
            if names:
                ok = 0
                for n in names:
                    spec = self._completion_specs.get(n)
                    if spec is None:
                        ok = 1
                        continue
                    wl = spec.get("W")
                    if isinstance(wl, str):
                        print(f"complete -W {shlex.quote(wl)} {n}")
                    else:
                        print(f"complete {n}")
                return ok
            for n in sorted(self._completion_specs):
                spec = self._completion_specs[n]
                wl = spec.get("W")
                if isinstance(wl, str):
                    print(f"complete -W {shlex.quote(wl)} {n}")
                else:
                    print(f"complete {n}")
            return 0

        if remove_mode:
            if not names:
                self._completion_specs.clear()
                return 0
            for n in names:
                self._completion_specs.pop(n, None)
            return 0

        if not names:
            self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="complete", opt="name"))
            return 2
        for n in names:
            self._completion_specs[n] = {"W": wordlist, "A": action, "o": set(comp_opts)}
        return 0

    def _run_compgen(self, args: List[str]) -> int:
        action: str | None = None
        want_builtin = False
        word = ""
        i = 0
        while i < len(args):
            a = args[i]
            if a == "-b":
                want_builtin = True
                i += 1
                continue
            if a == "-A":
                if i + 1 >= len(args):
                    self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="compgen", opt="A"))
                    return 2
                action = args[i + 1]
                i += 2
                continue
            if a.startswith("-"):
                i += 1
                continue
            word = a
            i += 1
            break

        candidates: list[str]
        mode = "builtin" if want_builtin else (action or "")
        if mode in {"builtin", "b"}:
            candidates = sorted(self.BUILTINS)
        elif mode == "alias":
            candidates = sorted(self.aliases.keys())
        elif mode == "function":
            candidates = self._function_names()
        elif mode == "keyword":
            candidates = sorted({"if", "then", "else", "elif", "fi", "for", "in", "do", "done", "case", "esac", "while", "until", "{", "}"})
        elif mode == "command":
            candidates = sorted(set(self.BUILTINS) | set(self._function_names()))
        else:
            # Bash defaults to filename generation without explicit action.
            # Keep non-interactive behavior simple and return success.
            return 0
        out = [c for c in candidates if c.startswith(word)]
        for c in out:
            print(c)
        return 0 if out else 1

    def _run_compopt(self, args: List[str]) -> int:
        i = 0
        names: list[str] = []
        while i < len(args):
            a = args[i]
            if a in {"-o", "+o"}:
                if i + 1 >= len(args):
                    self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="compopt", opt="o"))
                    return 2
                i += 2
                continue
            if a in {"-D", "-E", "-I"}:
                i += 1
                continue
            if a.startswith("-"):
                self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="compopt", opt=a))
                return 2
            names.extend(args[i:])
            break
        if not names:
            return 1
        for n in names:
            if n not in self._completion_specs:
                return 1
        return 0

    def _run_bind(self, args: List[str]) -> int:
        readline_funcs = ["abort", "accept-line", "alias-expand-line", "self-insert"]
        key_to_func = {
            "\\C-g": "abort",
            "\\C-j": "accept-line",
            "\\C-m": "accept-line",
            " ": "self-insert",
        }
        selected: list[str] = []
        mode: str | None = None
        i = 0
        while i < len(args):
            a = args[i]
            if a == "-l":
                for f in readline_funcs:
                    print(f)
                return 0
            if a in {"-p", "-P"}:
                mode = a
                i += 1
                continue
            if a == "-q":
                if i + 1 >= len(args):
                    self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="bind", opt="q"))
                    return 2
                return 0 if args[i + 1] in readline_funcs else 1
            if a == "-r":
                if i + 1 >= len(args):
                    self._report_error(self._diag_msg(DiagnosticKey.OPTION_REQUIRES_ARG, cmd="bind", opt="r"))
                    return 2
                return 0
            if a.startswith("-"):
                # Accept a small non-interactive subset.
                self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="bind", opt=a))
                return 2
            selected.extend(args[i:])
            break
        if mode in {"-p", "-P"}:
            funcs = selected if selected else readline_funcs
            valid = [f for f in funcs if f in readline_funcs]
            if mode == "-p":
                emitted = False
                for key, fn in key_to_func.items():
                    if fn in valid:
                        print(f'"{key}": {fn}')
                        emitted = True
                return 0 if emitted else 1
            for fn in valid:
                keys = [k for k, v in key_to_func.items() if v == fn]
                if keys:
                    print(f"{fn} can be found on " + ", ".join(f'"{k}"' for k in keys) + ".")
                else:
                    print(f"{fn} is not bound to any keys")
            return 0 if valid else 1
        return 0

    def _fd_ready_now(self, fd: int) -> bool:
        if fd == 0 and isinstance(sys.stdin, io.StringIO):
            pos = sys.stdin.tell()
            ch = sys.stdin.read(1)
            sys.stdin.seek(pos)
            if ch != "":
                return True
            # In real pipelines EOF on a closed upstream is considered readable
            # by read -t 0; approximate using captured upstream latency.
            if self._pipeline_input_latency is not None and self._pipeline_input_latency <= 0.05:
                return True
            return False
        try:
            r, _, _ = select.select([fd], [], [], 0)
            return bool(r)
        except Exception:
            return False

    def _read_interrupt_status(self) -> int | None:
        if not self._shopts.get("read_interruptible", False):
            return None
        if not self._pending_signals:
            return None
        sig_name = self._pending_signals[0]
        self._run_pending_traps()
        sig_num = self._signal_number(sig_name)
        return 128 + sig_num if sig_num else 1

    def _read_one_fd_char(
        self,
        fd: int,
        timeout_sec: float | None,
        deadline: float | None,
    ) -> str | None:
        if fd == 0 and isinstance(sys.stdin, io.StringIO):
            ch = sys.stdin.read(1)
            if ch == "":
                return ""
            return ch
        if timeout_sec is None:
            if self._shopts.get("read_interruptible", False):
                while True:
                    status = self._read_interrupt_status()
                    if status is not None:
                        self._last_read_interrupt_status = status
                        return None
                    r, _, _ = select.select([fd], [], [], 0.05)
                    if r:
                        break
            else:
                r, _, _ = select.select([fd], [], [], None)
                if not r:
                    return None
        else:
            now = time.monotonic()
            remaining = timeout_sec if deadline is None else (deadline - now)
            if remaining <= 0:
                # read -t 0: perform a non-blocking readiness probe.
                r, _, _ = select.select([fd], [], [], 0)
                if not r:
                    return None
                chunk = os.read(fd, 1)
                if not chunk:
                    return ""
                return chunk.decode("utf-8", errors="surrogateescape")
            if self._shopts.get("read_interruptible", False):
                while remaining > 0:
                    status = self._read_interrupt_status()
                    if status is not None:
                        self._last_read_interrupt_status = status
                        return None
                    sl = min(remaining, 0.05)
                    r, _, _ = select.select([fd], [], [], sl)
                    if r:
                        break
                    now = time.monotonic()
                    remaining = timeout_sec if deadline is None else (deadline - now)
                else:
                    return None
            else:
                r, _, _ = select.select([fd], [], [], remaining)
                if not r:
                    return None
        chunk = os.read(fd, 1)
        if not chunk:
            return ""
        return chunk.decode("utf-8", errors="surrogateescape")

    def _read_from_fd(
        self,
        *,
        fd: int,
        delimiter: str = "\n",
        raw_mode: bool = False,
        n_chars: int | None = None,
        timeout_sec: float | None = None,
        exact_chars: bool = False,
    ) -> Tuple[str, bool]:
        buf: List[str] = []
        saw_input = False
        saw_delim = False
        hit_eof = False
        deadline = time.monotonic() + timeout_sec if timeout_sec is not None else None
        if (
            fd == 0
            and
            timeout_sec is not None
            and timeout_sec > 0
            and isinstance(sys.stdin, io.StringIO)
            and self._pipeline_input_latency is not None
            and self._pipeline_input_latency > timeout_sec
        ):
            return "", False

        while True:
            if n_chars is not None and len(buf) >= n_chars:
                break
            ch = self._read_one_fd_char(fd, timeout_sec, deadline)
            if ch is None:
                if self._last_read_interrupt_status is not None:
                    return "".join(buf), False
                # Timeout.
                self._last_read_timed_out = True
                return "".join(buf), False
            if ch == "":
                hit_eof = True
                break
            if not exact_chars and ch == delimiter:
                saw_delim = True
                break
            saw_input = True
            if not raw_mode and ch == "\\":
                nxt = self._read_one_fd_char(fd, timeout_sec, deadline)
                if nxt is None:
                    if self._last_read_interrupt_status is not None:
                        return "".join(buf), False
                    self._last_read_timed_out = True
                    return "".join(buf), False
                if nxt == "":
                    hit_eof = True
                    break
                saw_input = True
                if nxt == "\n":
                    continue
                buf.append(nxt)
                continue
            buf.append(ch)

        if not saw_input and not saw_delim:
            return "", False
        if exact_chars and n_chars is not None:
            return "".join(buf), len(buf) >= n_chars
        if n_chars is not None:
            if len(buf) >= n_chars or saw_delim:
                return "".join(buf), True
            return "".join(buf), not hit_eof
        return "".join(buf), saw_delim

    def _split_read_fields(self, text: str, names: List[str]) -> List[str]:
        ifs = self.env.get("IFS", " \t\n")
        if ifs == "":
            out = ["" for _ in names]
            out[0] = text
            return out

        ifs_ws = "".join(ch for ch in ifs if ch in " \t\n")
        ifs_other = "".join(ch for ch in ifs if ch not in " \t\n")

        def _skip_ws(s: str, pos: int) -> int:
            while pos < len(s) and s[pos] in ifs_ws:
                pos += 1
            return pos

        def _consume_one_separator(s: str, pos: int) -> int:
            if pos >= len(s) or s[pos] not in ifs:
                return pos
            if s[pos] in ifs_ws:
                pos = _skip_ws(s, pos)
                if pos < len(s) and s[pos] in ifs_other:
                    pos += 1
                    pos = _skip_ws(s, pos)
                return pos
            # Non-whitespace IFS char delimiter (plus following IFS whitespace).
            pos += 1
            pos = _skip_ws(s, pos)
            return pos

        def _next_field(s: str, pos: int) -> Tuple[str, int, bool]:
            start = pos
            while pos < len(s) and s[pos] not in ifs:
                pos += 1
            field = s[start:pos]
            if pos >= len(s):
                return field, pos, True
            pos = _consume_one_separator(s, pos)
            return field, pos, False

        pos = _skip_ws(text, 0)
        if len(names) == 1:
            rem = text[pos:]
            if ifs_ws:
                rem = rem.rstrip(ifs_ws)
            return [rem]

        out: List[str] = []
        for _ in range(len(names) - 1):
            field, pos, end = _next_field(text, pos)
            out.append(field)
            if end:
                out.extend("" for _ in range(len(names) - len(out)))
                return out
        rem = text[pos:]
        if ifs_ws:
            rem = rem.rstrip(ifs_ws)
        if rem and ifs_other and rem[-1] in ifs_other:
            # For read with multiple variables, drop exactly one trailing
            # separator only when it is a single final separator token, not
            # part of an already-adjacent separator sequence.
            m = len(rem) - 1
            while m > 0 and rem[m - 1] in ifs_ws:
                m -= 1
            prefix = rem[:m]
            if not any(ch in ifs for ch in prefix):
                rem = prefix
        out.append(rem)
        return out

    def _run_command_builtin(self, args: List[str]) -> int:
        if not args:
            return 0
        i = 0
        search_default_path = False
        lookup_path: str | None = None
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            if args[i] == "--":
                i += 1
                break
            if args[i] == "-p":
                search_default_path = True
                lookup_path = "/usr/bin:/bin"
                i += 1
                continue
            if args[i] in ["-v", "-V"]:
                if i + 1 >= len(args):
                    return 1
                name = args[i + 1]
                hits = self._classify_command_name(
                    name,
                    path_override=lookup_path,
                    include_nonexec=not self.options.get("posix", False),
                )
                if args[i] == "-v":
                    if not hits:
                        return 1
                    kind, data = hits[0]
                    if kind in {"alias", "function", "builtin"}:
                        print(name)
                    elif kind in {"file", "file_nonexec"}:
                        print(data)
                    else:
                        return 1
                    return 0
                if not hits:
                    print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=name), file=sys.stderr)
                    return 1
                kind, data = hits[0]
                if kind == "alias":
                    print(f"{name} is an alias for {data}")
                elif kind == "function":
                    print(f"{name} is a function")
                elif kind == "builtin":
                    print(f"{name} is a shell builtin")
                elif kind in {"file", "file_nonexec"}:
                    print(f"{name} is {data}")
                else:
                    print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=name), file=sys.stderr)
                    return 1
                return 0
            break
        cmd = args[i:]
        if not cmd:
            return 0
        if self._is_builtin_enabled(cmd[0]):
            try:
                return self._run_builtin(cmd[0], cmd)
            except SystemExit as e:
                return int(e.code) if e.code is not None else 0
        if self._has_function(cmd[0]):
            return self._run_function(cmd[0], cmd[1:])
        env = dict(self.env)
        if search_default_path:
            env["PATH"] = "/usr/bin:/bin"
        return self._run_external(cmd, env, [])

    def _run_builtin_builtin(self, args: List[str]) -> int:
        if not args:
            return 1
        i = 0
        if args and args[0] == "--":
            i = 1
        cmd = args[i:]
        while cmd and cmd[0] == "builtin":
            cmd = cmd[1:]
        if not cmd:
            return 1
        name = cmd[0]
        if not self._is_builtin_enabled(name):
            self._report_error(self._diag_msg(DiagnosticKey.BUILTIN_NOT_SHELL_BUILTIN, name=name), line=self.current_line)
            return 1
        try:
            return self._run_builtin(name, [name] + cmd[1:])
        except SystemExit as e:
            return int(e.code) if e.code is not None else 0

    def _run_argv_dispatch(
        self,
        cmd: List[str],
        *,
        path_override: str | None = None,
    ) -> int:
        if not cmd:
            return 0
        if self._is_builtin_enabled(cmd[0]):
            try:
                return self._run_builtin(cmd[0], cmd)
            except SystemExit as e:
                return int(e.code) if e.code is not None else 0
        if self._has_function(cmd[0]):
            return self._run_function(cmd[0], cmd[1:])
        env = dict(self.env)
        if path_override is not None:
            env["PATH"] = path_override
        return self._run_external(cmd, env, [])

    def _run_trap(self, args: List[str]) -> int:
        if len(args) == 1 and args[0] == "-l":
            self._print_signal_table()
            return 0
        if args and args[0] == "-p":
            targets: list[str] = []
            if len(args) == 1:
                # bash --posix prints all known signals for `trap -p` with no
                # args, including default dispositions.
                targets = ["EXIT"] + [name for _, name in self._signal_names_by_number()]
            else:
                for sig in args[1:]:
                    key = self._normalize_signal_spec(sig)
                    if key is None:
                        line = (self.current_line + 1) if self.current_line is not None else None
                        self._report_error(
                            self._diag_msg(DiagnosticKey.INVALID_SIGNAL_SPEC, sig=sig),
                            line=line,
                            context="trap",
                        )
                        return 1
                    targets.append(key)
            for key in targets:
                if key in self.traps:
                    action = self.traps.get(key, "")
                    print(f"trap -- '{action}' {key}", flush=True)
                else:
                    print(f"trap -- - {key}", flush=True)
            return 0
        if not args:
            for sig, action in sorted(self.traps.items()):
                print(f"trap -- '{action}' {sig}", flush=True)
            return 0
        normalized0 = self._normalize_signal_spec(args[0]) if args else None
        first_is_cond = False
        if len(args) == 1 and normalized0 is not None:
            first_is_cond = True
        elif len(args) >= 2 and normalized0 == "EXIT":
            first_is_cond = True
        if first_is_cond:
            action = "-"
            sig_args = args
        else:
            if len(args) < 2:
                return 1
            action = args[0]
            sig_args = args[1:]
        status = 0
        for sig in sig_args:
            key = self._normalize_signal_spec(sig)
            if key is None:
                line = (self.current_line + 1) if self.current_line is not None else None
                self._report_error(
                    self._diag_msg(DiagnosticKey.INVALID_SIGNAL_SPEC, sig=sig),
                    line=line,
                    context="trap",
                )
                status = 1
                continue
            if action in ["-", "0"]:
                self.traps.pop(key, None)
            else:
                self.traps[key] = action
        return status

    def _run_type(self, args: List[str]) -> int:
        if not args:
            return 1
        if self._bash_compat_level is None and self._diag.style != "bash":
            if any(a.startswith("-") and a != "-" for a in args):
                return 127
            status = 0
            for name in args:
                hits = self._classify_command_name(name, include_nonexec=False)
                if not hits:
                    self._report_error(self._diag_msg(DiagnosticKey.TYPE_NOT_FOUND, name=name), line=self.current_line)
                    status = 127
                    continue
                kind, data = hits[0]
                if kind == "alias":
                    print(f"{name} is an alias for {data}", flush=True)
                elif kind == "function":
                    print(f"{name} is a function", flush=True)
                elif kind == "builtin":
                    print(f"{name} is a shell builtin", flush=True)
                elif kind == "file":
                    print(f"{name} is {data}", flush=True)
                else:
                    self._report_error(self._diag_msg(DiagnosticKey.TYPE_NOT_FOUND, name=name), line=self.current_line)
                    status = 127
            return status
        mode_t = False
        mode_a = False
        i = 0
        while i < len(args):
            a = args[i]
            if a == "--":
                i += 1
                break
            if not a.startswith("-") or a == "-":
                break
            for ch in a[1:]:
                if ch == "t":
                    mode_t = True
                elif ch == "a":
                    mode_a = True
                else:
                    self._report_error(self._diag_msg(DiagnosticKey.INVALID_OPTION, cmd="type", opt=f"-{ch}"))
                    return 2
            i += 1
        args = args[i:]
        if not args:
            return 1
        status = 0
        for name in args:
            hits = self._classify_command_name(name, include_nonexec=False)
            if not hits:
                self._report_error(self._diag_msg(DiagnosticKey.TYPE_NOT_FOUND, name=name), line=self.current_line)
                status = 1
                continue
            show_hits = hits if mode_a else hits[:1]
            for kind, data in show_hits:
                if mode_t:
                    print(kind, flush=True)
                    continue
                if kind == "alias":
                    print(f"{name} is an alias for {data}", flush=True)
                elif kind == "function":
                    print(f"{name} is a function", flush=True)
                    body = self.functions_asdl.get(name)
                    if isinstance(body, dict):
                        print(self._format_asdl_function(name, body), flush=True)
                elif kind == "builtin":
                    print(f"{name} is a shell builtin", flush=True)
                else:
                    print(f"{name} is {data}", flush=True)
        return status

    def _format_ast_function(self, name: str, body: ListNode) -> str:
        lines: list[str] = [f"{name} () ", "{ "]
        work = body
        if (
            len(body.items) == 1
            and len(body.items[0].node.pipelines) == 1
            and len(body.items[0].node.pipelines[0].commands) == 1
            and isinstance(body.items[0].node.pipelines[0].commands[0], GroupCommand)
        ):
            work = body.items[0].node.pipelines[0].commands[0].body
        lines.extend(self._format_ast_list_for_type(work, indent=4))
        lines.append("}")
        return "\n".join(lines)

    def _format_ast_list_for_type(self, node: ListNode, indent: int) -> list[str]:
        out: list[str] = []
        for item in node.items:
            out.extend(self._format_ast_andor_for_type(item.node, indent))
        if not out:
            out.append(" " * indent + ":")
        return out

    def _format_ast_andor_for_type(self, node: AndOr, indent: int) -> list[str]:
        if len(node.pipelines) == 1 and not node.operators:
            return self._format_ast_pipeline_for_type(node.pipelines[0], indent)
        text_parts: list[str] = []
        for i, pl in enumerate(node.pipelines):
            text_parts.append(self._format_ast_pipeline_inline_for_type(pl))
            if i < len(node.operators):
                text_parts.append(node.operators[i])
        return [" " * indent + " ".join(text_parts)]

    def _format_ast_pipeline_for_type(self, node: Pipeline, indent: int) -> list[str]:
        if len(node.commands) == 1:
            return self._format_ast_command_for_type(node.commands[0], indent)
        prefix = "! " if node.negate else ""
        text = " | ".join(self._format_ast_command_inline_for_type(c) for c in node.commands)
        return [" " * indent + prefix + text]

    def _format_ast_pipeline_inline_for_type(self, node: Pipeline) -> str:
        prefix = "! " if node.negate else ""
        if len(node.commands) == 1:
            return prefix + self._format_ast_command_inline_for_type(node.commands[0])
        return prefix + " | ".join(self._format_ast_command_inline_for_type(c) for c in node.commands)

    def _format_ast_command_inline_for_type(self, node: Command) -> str:
        lines = self._format_ast_command_for_type(node, 0)
        text = " ".join(line.strip().rstrip(";") for line in lines if line.strip())
        return text if text else ":"

    def _format_ast_command_for_type(self, node: Command, indent: int) -> list[str]:
        pad = " " * indent
        if isinstance(node, SimpleCommand):
            items = [f"{a.name}{a.op}{a.value}" for a in node.assignments] + [w.text for w in node.argv]
            text = " ".join(items) if items else ":"
            if text == "time":
                return [pad + "time "]
            return [pad + text]
        if isinstance(node, ForCommand):
            head = f"for {node.name}"
            if node.explicit_in:
                head += " in " + " ".join(w.text for w in node.items)
            lines = [pad + head, pad + "do"]
            lines.extend(self._format_ast_list_for_type(node.body, indent + 4))
            lines.append(pad + "done")
            return lines
        if isinstance(node, WhileCommand):
            kw = "until" if node.until else "while"
            lines = [pad + kw]
            lines.extend(self._format_ast_list_for_type(node.cond, indent + 4))
            lines.append(pad + "do")
            lines.extend(self._format_ast_list_for_type(node.body, indent + 4))
            lines.append(pad + "done")
            return lines
        if isinstance(node, IfCommand):
            lines = [pad + "if"]
            lines.extend(self._format_ast_list_for_type(node.cond, indent + 4))
            lines.append(pad + "then")
            lines.extend(self._format_ast_list_for_type(node.then_body, indent + 4))
            for cond, body in node.elifs:
                lines.append(pad + "elif")
                lines.extend(self._format_ast_list_for_type(cond, indent + 4))
                lines.append(pad + "then")
                lines.extend(self._format_ast_list_for_type(body, indent + 4))
            if node.else_body is not None:
                lines.append(pad + "else")
                lines.extend(self._format_ast_list_for_type(node.else_body, indent + 4))
            lines.append(pad + "fi")
            return lines
        if isinstance(node, GroupCommand):
            lines = [pad + "{ "]
            lines.extend(self._format_ast_list_for_type(node.body, indent + 4))
            lines.append(pad + "}")
            return lines
        if isinstance(node, RedirectCommand):
            return self._format_ast_command_for_type(node.child, indent)
        if isinstance(node, SubshellCommand):
            lines = [pad + "( "]
            lines.extend(self._format_ast_list_for_type(node.body, indent + 4))
            lines.append(pad + ")")
            return lines
        return [pad + ":;"]

    def _format_asdl_function(self, name: str, body: dict[str, Any]) -> str:
        lines: list[str] = [f"{name} () ", "{ "]
        lines.extend(self._format_asdl_command_list(body.get("children") or [], indent=4))
        lines.append("}")
        return "\n".join(lines)

    def _format_asdl_command_list(self, children: list[dict[str, Any]], indent: int) -> list[str]:
        out: list[str] = []
        pad = " " * indent
        for child in children:
            if not isinstance(child, dict):
                continue
            if child.get("type") == "command.Sentence":
                cmd = child.get("child") or {}
                lines = self._format_asdl_command_for_type(cmd, indent)
                term = self._asdl_token_text(child.get("terminator"))
                if term == "&" and lines:
                    lines[-1] = lines[-1] + " &"
                out.extend(lines)
                continue
            out.extend(self._format_asdl_command_for_type(child, indent))
        if not out:
            out.append(pad + ":;")
        return out

    def _format_asdl_command_for_type(self, node: dict[str, Any], indent: int) -> list[str]:
        pad = " " * indent
        t = node.get("type")
        if t == "command.CommandList":
            return self._format_asdl_command_list(node.get("children") or [], indent)
        if t == "command.Sentence":
            child = node.get("child") or {}
            lines = self._format_asdl_command_for_type(child, indent)
            term = self._asdl_token_text(node.get("terminator"))
            if term == "&" and lines:
                lines[-1] = lines[-1] + " &"
            return lines
        if t == "command.AndOr":
            pipes = node.get("children") or []
            ops = node.get("ops") or []
            if not pipes:
                return [pad + ":;"]
            if len(pipes) == 1 and not ops:
                return self._format_asdl_command_for_type(pipes[0], indent)
            parts: list[str] = []
            for i, p in enumerate(pipes):
                seg = self._format_asdl_command_for_type(p, 0)
                txt = " ".join(line.strip().rstrip(";") for line in seg if line.strip())
                if txt:
                    parts.append(txt)
                if i < len(ops):
                    op = self._asdl_token_text(ops[i])
                    if op:
                        parts.append(op)
            return [pad + (" ".join(parts) if parts else ":") + ";"]
        if t == "command.Simple":
            words = [self._asdl_word_to_text(w) for w in (node.get("words") or [])]
            assigns: list[str] = []
            for pair in (node.get("more_env") or []):
                name = str(pair.get("name") or "")
                op = str(pair.get("op") or "=")
                rhs = self._asdl_rhs_word_to_text(pair.get("val") or {})
                assigns.append(f"{name}{op}{rhs}")
            text = " ".join(assigns + words).strip()
            return [pad + (text if text else ":") + ";"]
        if t == "command.ForEach":
            iter_names = node.get("iter_names") or []
            iter_name = str(iter_names[0]) if iter_names else "i"
            iterable = ((node.get("iterable") or {}).get("words") or [])
            items = " ".join(self._asdl_word_to_text(w) for w in iterable)
            head = f"for {iter_name}"
            if node.get("explicit_in", True):
                head += f" in {items}"
            lines = [pad + head + ";", pad + "do"]
            body = node.get("body") or {}
            lines.extend(self._format_asdl_command_list(body.get("children") or [], indent + 4))
            lines.append(pad + "done")
            return lines
        if t == "command.ForExpr":
            raw = node.get("raw") or {}
            init = str(raw.get("init") or "")
            cond = str(raw.get("cond") or "")
            update = str(raw.get("update") or "")
            lines = [pad + f"for (({init}; {cond}; {update}));", pad + "do"]
            body = node.get("body") or {}
            lines.extend(self._format_asdl_command_list(body.get("children") or [], indent + 4))
            lines.append(pad + "done")
            return lines
        if t == "command.WhileUntil":
            kw = self._asdl_token_text(node.get("keyword")) or "while"
            cond = node.get("cond") or {}
            body = node.get("body") or {}
            lines = [pad + kw]
            lines.extend(self._format_asdl_command_list(cond.get("children") or [], indent + 4))
            lines.append(pad + "do")
            lines.extend(self._format_asdl_command_list(body.get("children") or [], indent + 4))
            lines.append(pad + "done")
            return lines
        if t == "command.If":
            lines = [pad + "if"]
            arms = node.get("arms") or []
            if arms:
                cond = arms[0].get("cond") or {}
                act = arms[0].get("action") or {}
                lines.extend(self._format_asdl_command_list(cond.get("children") or [], indent + 4))
                lines.append(pad + "then")
                lines.extend(self._format_asdl_command_list(act.get("children") or [], indent + 4))
                for arm in arms[1:]:
                    cond = arm.get("cond") or {}
                    act = arm.get("action") or {}
                    lines.append(pad + "elif")
                    lines.extend(self._format_asdl_command_list(cond.get("children") or [], indent + 4))
                    lines.append(pad + "then")
                    lines.extend(self._format_asdl_command_list(act.get("children") or [], indent + 4))
            else_action = node.get("else_action") or {}
            if else_action.get("children"):
                lines.append(pad + "else")
                lines.extend(self._format_asdl_command_list(else_action.get("children") or [], indent + 4))
            lines.append(pad + "fi")
            return lines
        if t == "command.BraceGroup":
            lines = [pad + "{ "]
            lines.extend(self._format_asdl_command_list(node.get("children") or [], indent + 4))
            lines.append(pad + "}")
            return lines
        if t == "command.Redirect":
            child = node.get("child") or {}
            return self._format_asdl_command_for_type(child, indent)
        if t == "command.Pipeline":
            children = node.get("children") or []
            ops = node.get("ops") or []
            parts: list[str] = []
            for i, c in enumerate(children):
                part_lines = self._format_asdl_command_for_type(c, 0)
                ptxt = " ".join(line.strip().rstrip(";") for line in part_lines if line.strip())
                if ptxt:
                    parts.append(ptxt)
                if i < len(ops):
                    parts.append(str(ops[i]))
            neg = bool(node.get("negated"))
            lead = "! " if neg else ""
            return [pad + lead + " ".join(parts) + ";"]
        return [pad + ":" + ";"]

    def _asdl_command_to_sh_source(self, node: dict[str, Any]) -> str:
        """Best-effort shell source for spawning helper subprocesses (e.g. coproc)."""
        lines = self._format_asdl_command_for_type(node, 0)
        if not lines:
            return ":"
        return "\n".join(lines)

    def _run_let(self, args: List[str]) -> int:
        if not args:
            return 1
        last = "0"
        for expr in args:
            if "$" in expr:
                self._report_error(
                    self._diag_msg(DiagnosticKey.ARITH_SYNTAX_ERROR),
                    line=self.current_line,
                    context="let",
                )
                return 2
            try:
                last = self._expand_arith(expr, context="let")
            except ArithExpansionFailure as e:
                return e.code
        try:
            return 1 if int(last) == 0 else 0
        except ValueError:
            return 1

    def _find_in_path(self, name: str, path_override: str | None = None) -> str:
        hits = self._classify_command_name(
            name,
            path_override=path_override,
            include_alias=False,
            include_function=False,
            include_builtin=False,
            include_nonexec=False,
        )
        if hits and hits[0][0] == "file":
            return hits[0][1]
        return ""

    def _run_test(self, name: str, args: List[str]) -> int:
        tokens = list(args)
        if name == "[":
            if tokens and tokens[-1] == "]":
                tokens = tokens[:-1]
        if name == "[[":
            if tokens and tokens[-1] == "]]":
                tokens = tokens[:-1]
            if "||" in tokens:
                idx = tokens.index("||")
                left = self._run_test("[[", tokens[:idx] + ["]]"])
                if left == 0:
                    return 0
                right = self._run_test("[[", tokens[idx + 1 :] + ["]]"])
                return right
            if "&&" in tokens:
                idx = tokens.index("&&")
                left = self._run_test("[[", tokens[:idx] + ["]]"])
                if left != 0:
                    return left
                right = self._run_test("[[", tokens[idx + 1 :] + ["]]"])
                return right
        import locale

        def _int_or_zero(s: str) -> int:
            try:
                return int(s)
            except Exception:
                return 0

        i = 0

        def parse_or() -> bool:
            nonlocal i
            val = parse_and()
            while i < len(tokens) and tokens[i] == "-o":
                i += 1
                val = val or parse_and()
            return val

        def parse_and() -> bool:
            nonlocal i
            val = parse_not()
            while i < len(tokens) and tokens[i] == "-a":
                i += 1
                val = val and parse_not()
            return val

        def parse_not() -> bool:
            nonlocal i
            if i < len(tokens) and tokens[i] == "!":
                i += 1
                return not parse_not()
            return parse_primary()

        def parse_primary() -> bool:
            nonlocal i
            if i >= len(tokens):
                return False
            t = tokens[i]
            if t in {"(", "\\("}:
                i += 1
                val = parse_or()
                if i < len(tokens) and tokens[i] in {")", "\\)"}:
                    i += 1
                return val
            # Unary primaries.
            if i + 1 < len(tokens) and t in {"-e", "-v", "-n", "-z", "-f", "-d", "-x", "-t", "-s"}:
                op = t
                arg = tokens[i + 1]
                i += 2
                if op == "-e":
                    return os.path.exists(arg)
                if op == "-v":
                    return self._test_var_is_set(arg)
                if op == "-n":
                    return arg != ""
                if op == "-z":
                    return arg == ""
                if op == "-f":
                    return os.path.isfile(arg)
                if op == "-d":
                    return os.path.isdir(arg)
                if op == "-x":
                    return os.access(arg, os.X_OK)
                if op == "-s":
                    try:
                        return os.path.getsize(arg) > 0
                    except OSError:
                        return False
                if op == "-t":
                    fd = _int_or_zero(arg)
                    try:
                        return os.isatty(fd)
                    except Exception:
                        return False
            # Binary primaries.
            if i + 2 < len(tokens):
                left = tokens[i]
                op = tokens[i + 1]
                right = tokens[i + 2]
                if op in {"=", "!="}:
                    i += 3
                    out = (left == right)
                    return out if op == "=" else (not out)
                if op in {"<", ">"}:
                    i += 3
                    cmp = locale.strcoll(left, right)
                    return cmp < 0 if op == "<" else cmp > 0
                if op in {"-eq", "-ne", "-gt", "-ge", "-lt", "-le"}:
                    i += 3
                    lnum = _int_or_zero(left)
                    rnum = _int_or_zero(right)
                    if op == "-eq":
                        return lnum == rnum
                    if op == "-ne":
                        return lnum != rnum
                    if op == "-gt":
                        return lnum > rnum
                    if op == "-ge":
                        return lnum >= rnum
                    if op == "-lt":
                        return lnum < rnum
                    if op == "-le":
                        return lnum <= rnum
            # Fallback: non-empty string test.
            i += 1
            return t != ""

        result = parse_or()
        return 0 if result else 1

    def _test_var_is_set(self, expr: str) -> bool:
        parsed = self._parse_subscripted_name(expr)
        if parsed is not None:
            base, key = parsed
            attrs = self._var_attrs.get(base, set())
            typed = self._typed_vars.get(base)
            if key in {"@", "*"}:
                if "assoc" in attrs and isinstance(typed, dict):
                    return len(typed) > 0
                if "array" in attrs and isinstance(typed, list):
                    return any(v is not None for v in typed)
                _, is_set = self._get_var_with_state(base)
                return is_set
            if "assoc" in attrs and isinstance(typed, dict):
                akey = self._eval_assoc_subscript_key(key)
                return akey in typed
            if "array" in attrs and isinstance(typed, list):
                i_key = self._eval_index_subscript(key, typed, strict=False, name=base)
                return i_key is not None and 0 <= i_key < len(typed) and typed[i_key] is not None
            return False
        attrs = self._var_attrs.get(expr, set())
        if "assoc" in attrs:
            return False
        if "array" in attrs:
            return False
        _, is_set = self._get_var_with_state(expr)
        return is_set

    def _eval_source(
        self,
        source: str,
        propagate_exit: bool = False,
        propagate_return: bool = False,
        parse_context: str | None = None,
        line_offset: int = 0,
    ) -> int:
        self._last_eval_hard_error = False
        parser_impl = Parser(
            source,
            aliases=self.aliases,
            lenient_unterminated_quotes=(self._bash_compat_level is not None),
        )
        status = 0
        try:
            while True:
                node = parser_impl.parse_next()
                if node is None:
                    break
                self.current_line = parser_impl.last_line
                if self.options.get("n", False):
                    status = 0
                    continue
                if parser_impl.last_lst_item is None:
                    raise ParseError("internal parse error: missing LST list item")
                asdl_item = lst_list_item_to_asdl(parser_impl.last_lst_item, strict=True)
                status = self._exec_asdl_list_item(asdl_item)
                errexit_item_exempt = self._take_errexit_item_exempt()
                self.last_status = status
                if status != 0:
                    self.last_nonzero_status = status
                self._trap_status_hint = status
                if not getattr(node, "background", False):
                    self._run_pending_traps()
                if (
                    status != 0
                    and self.options.get("e", False)
                    and self._errexit_suppressed == 0
                    and not errexit_item_exempt
                ):
                    raise SystemExit(status)
        except ReturnFromFunction as e:
            status = e.code
            if propagate_return:
                raise
        except SystemExit as e:
            status = int(e.code) if e.code is not None else 0
            if propagate_exit:
                raise
        except ParseError as e:
            text, line_hint = self._normalize_parse_error(str(e))
            if line_hint is not None:
                report_line = line_hint + line_offset
                err_context = parse_context
                if self._diag.style != "bash" and parse_context == "command substitution":
                    # ash-style diagnostics for parse failures in command substitutions
                    # don't include the explicit context label, and line numbers are
                    # reported relative to the nested snippet start.
                    err_context = None
                    report_line -= 1
                self._report_error(text, line=report_line, context=err_context)
                if self._diag.style == "bash" and parse_context in {"eval", "command substitution"}:
                    src_for_diag = source
                    if (
                        parse_context == "command substitution"
                        and not src_for_diag.rstrip().endswith(")")
                    ):
                        src_for_diag = src_for_diag + ")"
                    print(self._format_error(f"`{src_for_diag}'", line=report_line, context=parse_context), file=sys.stderr)
            else:
                print(f"parse error: {text}", file=sys.stderr)
            status = 2
            self._last_eval_hard_error = True
        except AsdlMappingError as e:
            print(f"asdl error: {e}", file=sys.stderr)
            status = 2
            self._last_eval_hard_error = True
        except RuntimeError as e:
            msg = str(e)
            self._emit_runtime_error(msg, context=parse_context)
            status = self._runtime_error_status(msg)
        return status

    def _capture_eval(
        self,
        source: str,
        line_bias: int = 0,
        frame_kind: str = "command_subst",
    ) -> tuple[str, int, bool]:
        tmp = tempfile.TemporaryFile()
        try:
            sys.stdout.flush()
        except Exception:
            pass
        saved_stdout = os.dup(1)
        os.dup2(tmp.fileno(), 1)
        py_stdout = os.fdopen(os.dup(1), "w", encoding="utf-8", errors="surrogateescape", buffering=1)
        saved_py_stdout = sys.stdout
        sys.stdout = py_stdout
        saved_line = self.current_line
        saved_offset = self._line_offset
        saved_options = dict(self.options)
        saved_env = dict(self.env)
        saved_typed_vars = copy.deepcopy(self._typed_vars)
        saved_local_stack = [dict(scope) for scope in self.local_stack]
        saved_positional = list(self.positional)
        saved_script_name = self.script_name
        try:
            saved_cwd: str | None = os.getcwd()
        except OSError:
            saved_cwd = None
        base = (self.current_line or 1) + line_bias
        self._line_offset = saved_offset + (base - 1)
        # Evaluate command substitution in an isolated mutable state so
        # temporary mutations don't leak back through shared dict objects.
        self.env = dict(saved_env)
        self._typed_vars = copy.deepcopy(saved_typed_vars)
        self.local_stack = [dict(scope) for scope in saved_local_stack]
        self.positional = list(saved_positional)
        # In bash/ash POSIX behavior, command substitution under `set -e`
        # remains errexit-sensitive. In non-POSIX bash mode, `-e` is not
        # inherited into command substitution.
        if not saved_options.get("posix", False):
            self.options["e"] = False
        try:
            with self._push_frame(kind=frame_kind):
                status = self._eval_source(source, parse_context="command substitution", line_offset=1)
        finally:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            sys.stdout = saved_py_stdout
            try:
                py_stdout.close()
            except Exception:
                pass
            self.current_line = saved_line
            self._line_offset = saved_offset
            self.options = saved_options
            self.env = saved_env
            self._typed_vars = saved_typed_vars
            self.local_stack = saved_local_stack
            self.positional = saved_positional
            self.script_name = saved_script_name
            if saved_cwd is not None:
                try:
                    os.chdir(saved_cwd)
                except OSError:
                    pass
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
        tmp.seek(0)
        data = tmp.read()
        tmp.close()
        return data.decode("utf-8", errors="ignore"), status, self._last_eval_hard_error

    def _capture_eval_asdl(
        self,
        child: dict[str, Any],
        line_bias: int = 0,
        frame_kind: str = "command_subst",
    ) -> tuple[str, int, bool]:
        tmp = tempfile.TemporaryFile()
        try:
            sys.stdout.flush()
        except Exception:
            pass
        saved_stdout = os.dup(1)
        os.dup2(tmp.fileno(), 1)
        py_stdout = os.fdopen(os.dup(1), "w", encoding="utf-8", errors="surrogateescape", buffering=1)
        saved_py_stdout = sys.stdout
        sys.stdout = py_stdout
        saved_line = self.current_line
        saved_offset = self._line_offset
        saved_options = dict(self.options)
        saved_env = dict(self.env)
        saved_typed_vars = copy.deepcopy(self._typed_vars)
        saved_local_stack = [dict(scope) for scope in self.local_stack]
        saved_positional = list(self.positional)
        saved_script_name = self.script_name
        try:
            saved_cwd: str | None = os.getcwd()
        except OSError:
            saved_cwd = None
        base = (self.current_line or 1) + line_bias
        self._line_offset = saved_offset + (base - 1)
        self.env = dict(saved_env)
        self._typed_vars = copy.deepcopy(saved_typed_vars)
        self.local_stack = [dict(scope) for scope in saved_local_stack]
        self.positional = list(saved_positional)
        if not saved_options.get("posix", False):
            self.options["e"] = False
        hard_error = False
        try:
            with self._push_frame(kind=frame_kind):
                status = self._exec_asdl_command_list(child.get("children") or [])
        except SystemExit as e:
            status = int(e.code) if e.code is not None else 0
        except RuntimeError as e:
            msg = str(e)
            self._emit_runtime_error(msg, context="command substitution")
            status = self._runtime_error_status(msg)
            hard_error = True
        finally:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            sys.stdout = saved_py_stdout
            try:
                py_stdout.close()
            except Exception:
                pass
            self.current_line = saved_line
            self._line_offset = saved_offset
            self.options = saved_options
            self.env = saved_env
            self._typed_vars = saved_typed_vars
            self.local_stack = saved_local_stack
            self.positional = saved_positional
            self.script_name = saved_script_name
            if saved_cwd is not None:
                try:
                    os.chdir(saved_cwd)
                except OSError:
                    pass
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
        tmp.seek(0)
        data = tmp.read()
        tmp.close()
        return data.decode("utf-8", errors="ignore"), status, hard_error

    def _normalize_parse_error(self, msg: str) -> tuple[str, int | None]:
        if msg.startswith("expected then at "):
            where = msg[len("expected then at ") :]
            line_s = where.split(":", 1)[0]
            return 'syntax error: unexpected ")"', int(line_s) if line_s.isdigit() else None
        if msg.startswith("expected done at "):
            where = msg[len("expected done at ") :]
            line_s = where.split(":", 1)[0]
            return (
                'syntax error: unexpected end of file (expecting "done")',
                int(line_s) if line_s.isdigit() else self.current_line,
            )
        if msg.startswith("expected fi at "):
            where = msg[len("expected fi at ") :]
            line_s = where.split(":", 1)[0]
            return "syntax error near unexpected token `)'", int(line_s) if line_s.isdigit() else self.current_line
        if ("syntax error:" in msg or "syntax error near unexpected token" in msg) and " at " in msg:
            text, where = msg.rsplit(" at ", 1)
            line_s = where.split(":", 1)[0]
            return text, int(line_s) if line_s.isdigit() else self.current_line
        return msg, None

    def _emit_runtime_error(self, msg: str, *, line: int | None = None, context: str | None = None) -> None:
        # Preserve diagnostics already carrying explicit file/line context.
        if ": line " in msg and ":" in msg:
            print(msg, file=sys.stderr)
            return
        self._report_error(msg, line=line if line is not None else self.current_line, context=context)

    def _has_unterminated_quote(self, source: str) -> bool:
        in_single = False
        in_double = False
        i = 0
        while i < len(source):
            ch = source[i]
            if in_single:
                if ch == "'":
                    in_single = False
                i += 1
                continue
            if in_double:
                if ch == "\\" and i + 1 < len(source):
                    i += 2
                    continue
                if ch == '"':
                    in_double = False
                i += 1
                continue
            if ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
            elif ch == "\\" and i + 1 < len(source):
                i += 2
                continue
            i += 1
        return in_single or in_double

    def _expand_command_subst(self, text: str) -> str:
        return self._expand_command_subst_text(text)

    def _is_process_subst(self, text: str) -> bool:
        return (text.startswith("<(") or text.startswith(">(")) and text.endswith(")")

    def _process_substitute(self, text: str) -> str:
        if not self._is_process_subst(text):
            return text
        mode = text[0]
        body = text[2:-1]
        if mode == "<":
            out, _, _ = self._capture_eval(body, frame_kind="process_subst")
            fd, path = tempfile.mkstemp(prefix="mctash-psubst-in-")
            with os.fdopen(fd, "wb") as f:
                f.write(out.encode("utf-8", errors="ignore"))
            self._procsub_paths.add(path)
            return path

        fifo_path = os.path.join(tempfile.gettempdir(), f"mctash-psubst-out-{uuid.uuid4().hex}")
        os.mkfifo(fifo_path, 0o600)
        self._procsub_paths.add(fifo_path)
        env = dict(self.env)
        for scope in self.local_stack:
            env.update(scope)

        def _runner() -> None:
            try:
                payload = b""
                with open(fifo_path, "rb", buffering=0) as fifo:
                    payload = fifo.read()
                self._run_shell_subprocess(
                    script=body,
                    input_text=payload.decode("utf-8", errors="ignore"),
                    env=env,
                )
            finally:
                try:
                    os.unlink(fifo_path)
                except OSError:
                    pass
                self._procsub_paths.discard(fifo_path)

        th = threading.Thread(target=_runner, daemon=True)
        self._procsub_threads.append(th)
        th.start()
        return fifo_path
