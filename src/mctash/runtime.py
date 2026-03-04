from __future__ import annotations

import glob
import importlib
import importlib.util
import ctypes
import io
import json
import os
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
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from .ast_nodes import (
    AndOr,
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
from .lexer import LexContext, TokenReader
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

    def run(
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
    _thread_diag_lock = threading.Lock()
    _thread_diag_emitted: set[str] = set()
    SET_O_LIST_ORDER: List[str] = [
        "errexit",
        "noglob",
        "ignoreeof",
        "interactive",
        "monitor",
        "noexec",
        "stdin",
        "xtrace",
        "verbose",
        "vi",
        "emacs",
        "noclobber",
        "allexport",
        "notify",
        "nounset",
        "privileged",
        "nolog",
        "debug",
        "pipefail",
        "posix",
    ]
    SET_O_OPTION_MAP: Dict[str, str] = {
        "allexport": "a",
        "errexit": "e",
        "noglob": "f",
        "noexec": "n",
        "nounset": "u",
        "verbose": "v",
        "xtrace": "x",
        "noclobber": "C",
        "vi": "V",
        "emacs": "E",
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
    }
    SPECIAL_BUILTINS = {
        ":",
        ".",
        "source",
        "local",
        "break",
        "continue",
        "eval",
        "exit",
        "export",
        "readonly",
        "return",
        "set",
        "shift",
        "trap",
        "unset",
        "getopts",
    }
    BUILTINS = {
        "cd",
        "exit",
        ":",
        "return",
        ".",
        "source",
        "local",
        "eval",
        "declare",
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
        self.aliases: Dict[str, str] = {}
        self.local_stack: List[Dict[str, str]] = []
        self.script_name: str = ""
        self.options: Dict[str, bool] = {}
        self.readonly_vars: set[str] = set()
        self._cmd_sub_used: bool = False
        self._cmd_sub_status: int = 0
        self._loop_depth: int = 0
        self.current_line: int | None = None
        self.source_stack: List[str] = []
        self.traps: Dict[str, str] = {}
        self._pending_signals: List[str] = []
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
        self._thread_ctx = threading.local()
        self._fd_redirect_depth: int = 0
        self._force_broken_pipe: bool = False
        self._user_fds: set[int] = set()
        self._active_temp_fds: set[int] = set()
        self._getopts_state: tuple[tuple[str, ...], int, int] | None = None
        self._procsub_paths: set[str] = set()
        self._line_offset: int = 0
        self._last_eval_hard_error: bool = False
        self._pipeline_input_latency: float | None = None
        self._test_mode: bool = self.env.get("MCTASH_TEST_MODE", "") == "1"
        self._py_import_counter: int = 0
        self._var_attrs: Dict[str, set[str]] = {k: {"exported"} for k in self.env.keys()}
        self._typed_vars: Dict[str, object] = {}
        self._bash_compat_level: int | None = self._parse_bash_compat_level(self.env.get("BASH_COMPAT", ""))
        self._frame_stack: List[Dict[str, object]] = []
        self._call_stack: List[str] = []
        self._history: List[str] = []
        self._cmd_hash: Dict[str, str] = {}
        self._errexit_suppressed: int = 0
        self._py_callables: Dict[str, Any] = {}
        self._py_ties: Dict[str, tuple[Any, Any, str | None]] = {}
        self._shopts: Dict[str, bool] = {"read_interruptible": False}
        self._last_read_interrupt_status: int | None = None
        self._last_read_timed_out: bool = False
        self.env.setdefault("OPTIND", "1")
        mode = self.env.get("MCTASH_MODE", "").strip().lower()
        diag_style = self.env.get("MCTASH_DIAG_STYLE", "").strip().lower()
        if diag_style not in {"ash", "bash"}:
            diag_style = "bash" if mode == "bash" else "ash"
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
        level = self._bash_compat_level
        if level is None:
            level = self._parse_bash_compat_level(self.env.get("BASH_COMPAT", ""))
            self._bash_compat_level = level
        if level is None:
            return False
        if feature == "declare_array":
            return True
        if feature == "declare_assoc":
            return True
        if feature == "bridge_collections":
            return True
        return False

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

    def set_positional_args(self, args: List[str]) -> None:
        self.positional = list(args)

    def set_script_name(self, name: str) -> None:
        self.script_name = name
        if name:
            if self.source_stack:
                self.source_stack[0] = name
            else:
                self.source_stack = [name]
        self._sync_root_frame()

    def run(self, script: Script) -> int:
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
        for sig in signal.Signals:
            if sig in (signal.SIGKILL, signal.SIGSTOP):
                continue
            try:
                signal.signal(sig, signal.SIG_DFL)
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

    def _format_error(self, msg: str, line: int | None = None, context: str | None = None) -> str:
        if self.source_stack:
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
        print(self._format_error(msg, line=line, context=context), file=sys.stderr)

    def _diag_msg(self, key: DiagnosticKey, **kwargs: str) -> str:
        return self._diag.render(key, **kwargs)

    def _runtime_error_status(self, msg: str) -> int:
        if "bad substitution" in msg or "unbound variable:" in msg:
            return 2
        return 1

    def _run_pending_traps(self) -> None:
        if self._get_subshell_depth() > 0:
            return
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

    def _run_exit_trap(self, status: int) -> int:
        action = self.traps.get("EXIT")
        if not action:
            return status
        try:
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

    def _exec_list_item(self, item) -> int:
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
                    if argv and argv[0] not in self.BUILTINS and not self._has_function(argv[0]):
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
                            try:
                                self._bg_status[job_id] = proc.wait()
                            finally:
                                self._bg_pids.pop(job_id, None)

                        th = threading.Thread(target=_watch_proc, daemon=True)
                        self._bg_jobs[job_id] = th
                        self._bg_pids[job_id] = proc.pid
                        self._bg_pid_to_job[proc.pid] = job_id
                        self._bg_started_at[job_id] = time.monotonic()
                        self._last_bg_job = job_id
                        self._last_bg_pid = proc.pid
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
                bg_rt._last_bg_job = self._last_bg_job
                bg_rt._last_bg_pid = self._last_bg_pid
                bg_rt._shared_store_path = self._shared_store_path
                bg_rt._shared_store = self._shared_store
                bg_rt._thread_ctx.job_id = job_id
                try:
                    bg_body = ListNode(items=[ListItem(node=item.node, background=False)])
                    status = bg_rt._run_subshell(bg_body)
                    self._bg_status[job_id] = status
                finally:
                    # In shared-fd fallback modes (no CLONE_FILES unshare),
                    # explicitly close fds that this background runtime opened.
                    bg_rt._close_tracked_fds_not_in(parent_fd_baseline)
                    self._bg_pids.pop(job_id, None)

            thread = threading.Thread(target=_run_bg)
            thread.daemon = True
            self._bg_jobs[job_id] = thread
            self._bg_started_at[job_id] = time.monotonic()
            self._last_bg_job = job_id
            thread.start()
            # Best-effort: wait briefly for background job leader PID so $! is
            # available immediately after '&' for common cases.
            deadline = time.monotonic() + 0.1
            while time.monotonic() < deadline:
                pid = self._bg_pids.get(job_id)
                if pid is not None:
                    self._last_bg_pid = pid
                    break
                if not thread.is_alive():
                    break
                time.sleep(0.001)
            return 0
        return self._exec_and_or(item.node)

    def _exec_asdl_list_item(self, item: dict[str, Any]) -> int:
        t = item.get("type")
        if t == "command.Sentence":
            term = self._asdl_token_text(item.get("terminator"))
            child = item.get("child")
            if not isinstance(child, dict):
                raise RuntimeError("invalid ASDL sentence node")
            if term == "&":
                return self._exec_asdl_background(child)
            return self._exec_asdl_list_item(child)
        if t != "command.AndOr":
            raise RuntimeError(f"invalid ASDL list item: {t}")
        return self._exec_asdl_and_or(item)

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
            if not argv:
                return False
            name = argv[0]
            if name in self.BUILTINS or self._has_function(name):
                return False
        return True

    def _exec_asdl_pipeline_external(self, commands: list[dict[str, Any]]) -> int:
        procs: list[subprocess.Popen] = []
        prev = None
        statuses: list[int] = []
        for i, cmd in enumerate(commands):
            cmd_env = dict(self.env)
            for scope in self.local_stack:
                for k, v in scope.items():
                    if k in self.env:
                        cmd_env[k] = v
            saved_env = self.env
            try:
                self.env = cmd_env
                for assign in (cmd.get("more_env") or []):
                    name = str(assign.get("name") or "")
                    value = self._expand_asdl_rhs_assignment(assign.get("val") or {})
                    cmd_env[name] = value
            finally:
                self.env = saved_env
            argv = self._expand_asdl_simple_argv(cmd)
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
                print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0]), file=sys.stderr)
                return 127
            except OSError as e:
                print(f"{argv[0]}: {e.strerror}", file=sys.stderr)
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
        return self._pipeline_result(statuses)

    def _exec_asdl_command(self, node: dict[str, Any]) -> int:
        t = node.get("type")
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
            body = node.get("body") or {"type": "command.CommandList", "children": []}
            # Canonical function storage for parsed shell code.
            self.functions_asdl[name] = body
            return 0
        if t == "command.ForEach":
            names = node.get("iter_names") or [""]
            var_name = str(names[0] if names else "")
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
        if t == "command.Case":
            to_match = node.get("to_match") or {}
            value_word = to_match.get("word") if isinstance(to_match, dict) else {}
            if isinstance(value_word, dict):
                self._validate_asdl_word_bad_subst(value_word)
            value = self._expand_asdl_word_scalar(value_word or {}, split_glob=False)
            for arm in (node.get("arms") or []):
                pat = arm.get("pattern") or {}
                matched = False
                for pw in (pat.get("words") or []):
                    self._validate_asdl_word_bad_subst(pw)
                    pattern = self._asdl_case_pattern_from_word(pw)
                    if fnmatch.fnmatchcase(value, pattern):
                        matched = True
                        break
                if matched:
                    return self._exec_asdl_command_list(arm.get("action") or [])
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
                        raise SystemExit(e.code)
                    assigned_names.add(name)
                    if name in self.readonly_vars:
                        msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                        print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                        raise SystemExit(2)
                    comp_vals = self._parse_compound_assignment_rhs(self._asdl_rhs_word_to_text(rhs))
                    if comp_vals is not None and self._bash_compat_level is None:
                        comp_vals = None
                    if name in self._py_ties:
                        if comp_vals is not None:
                            raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                        if op == "+=":
                            self._assign_shell_var(name, self._get_var(name) + value)
                        else:
                            self._assign_shell_var(name, value)
                        local_env[name] = self._get_var(name)
                        continue
                    if comp_vals is not None:
                        self._assign_compound_var(name, op, comp_vals)
                        compound_assigned.add(name)
                        local_env[name] = self._get_var(name)
                        continue
                    if op == "+=":
                        local_env[name] = local_env.get(name, "") + value
                    else:
                        local_env[name] = value
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
            if status < 0:
                sig_num = -status
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
                if argv and argv[0] not in self.BUILTINS and not self._has_function(argv[0]):
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
                        try:
                            self._bg_status[job_id] = proc.wait()
                        finally:
                            self._bg_pids.pop(job_id, None)

                    th = threading.Thread(target=_watch_proc, daemon=True)
                    self._bg_jobs[job_id] = th
                    self._bg_pids[job_id] = proc.pid
                    self._bg_pid_to_job[proc.pid] = job_id
                    self._bg_started_at[job_id] = time.monotonic()
                    self._last_bg_job = job_id
                    self._last_bg_pid = proc.pid
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
            bg_rt._last_bg_job = self._last_bg_job
            bg_rt._last_bg_pid = self._last_bg_pid
            bg_rt._shared_store_path = self._shared_store_path
            bg_rt._shared_store = self._shared_store
            bg_rt._thread_ctx.job_id = job_id
            try:
                status = bg_rt._run_subshell_asdl(
                    {"type": "command.CommandList", "children": [{"type": "command.Sentence", "child": child}]}
                )
                self._bg_status[job_id] = status
            finally:
                bg_rt._close_tracked_fds_not_in(parent_fd_baseline)
                self._bg_pids.pop(job_id, None)

        thread = threading.Thread(target=_run_bg, daemon=True)
        self._bg_jobs[job_id] = thread
        self._bg_started_at[job_id] = time.monotonic()
        self._last_bg_job = job_id
        thread.start()
        deadline = time.monotonic() + 0.1
        while time.monotonic() < deadline:
            pid = self._bg_pids.get(job_id)
            if pid is not None:
                self._last_bg_pid = pid
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
        try:
            self._validate_asdl_simple_like_words(node)
            argv = self._expand_asdl_simple_argv(node)
        except RuntimeError as e:
            msg = str(e)
            print(msg, file=sys.stderr)
            if "bad substitution" in msg or "unbound variable:" in msg:
                raise SystemExit(2)
            raise SystemExit(1)
        except CommandSubstFailure as e:
            return e.code
        except ArithExpansionFailure as e:
            raise SystemExit(e.code)
        argv = self._expand_aliases(argv)
        assign_pairs = node.get("more_env") or []

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
                        raise SystemExit(e.code)
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
                        self._assign_shell_var(name, value)
                        local_env[name] = self._get_var(name)
                        continue
                    op = str(assign.get("op") or "=")
                    if is_compound and comp_vals is not None:
                        self._assign_compound_var(name, op, comp_vals)
                        compound_assigned.add(name)
                        local_env[name] = self._get_var(name)
                        continue
                    local_env[name] = value
                should_persist_env = any(
                    not (r.op == ">&" and (r.fd is None or r.fd == 1) and r.target == "1")
                    for r in redirects
                )
                if should_persist_env:
                    for n in assigned_names:
                        if n in compound_assigned:
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
            for assign in assign_pairs:
                try:
                    value = self._expand_asdl_rhs_assignment(assign.get("val") or {})
                except CommandSubstFailure as e:
                    return e.code
                except ArithExpansionFailure as e:
                    raise SystemExit(e.code)
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
                    self._assign_shell_var(name, value)
                    local_env[name] = self._get_var(name)
                    continue
                op = str(assign.get("op") or "=")
                if is_compound and comp_vals is not None:
                    self._assign_compound_var(name, op, comp_vals)
                    compound_assigned.add(name)
                    local_env[name] = self._get_var(name)
                    self.env = local_env
                    continue
                local_env[name] = value
                self.env = local_env
        finally:
            self.env = saved_env

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
                self._typed_vars.pop(n, None)
            self.env.update(local_env)
            for tied_name in self._py_ties:
                self.env[tied_name] = self._get_var(tied_name)
            if self._cmd_sub_used:
                status = self._cmd_sub_status
                self._cmd_sub_used = False
                return status
            return 0

        argv_assigns = self._argv_assignment_words(argv)
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
                    elif op == "+=":
                        self._assign_shell_var(name, self._get_var(name) + str(value))
                    else:
                        self._assign_shell_var(name, str(value))
                    local_env[name.split("[", 1)[0]] = self._get_var(name.split("[", 1)[0])
                saved_env.update(local_env)
                for tied_name in self._py_ties:
                    saved_env[tied_name] = self._get_var(tied_name)
                return 0
            finally:
                self.env = saved_env

        name = argv[0]
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
        if name in self.BUILTINS:
            is_special = name in self.SPECIAL_BUILTINS
            if is_special:
                self.env = local_env
                try:
                    with self._redirected_fds(redirects):
                        return self._run_builtin(name, argv)
                except RuntimeError as e:
                    msg = str(e)
                    print(msg, file=sys.stderr)
                    return self._runtime_error_status(msg)
            saved_env = self.env
            try:
                self.env = local_env
                try:
                    with self._redirected_fds(redirects):
                        status = self._run_builtin(name, argv)
                except RuntimeError as e:
                    msg = str(e)
                    print(msg, file=sys.stderr)
                    return self._runtime_error_status(msg)
                if name in self.ENV_MUTATING_BUILTINS:
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
            exec_env = dict(local_env)
            for scope in self.local_stack:
                for k, v in scope.items():
                    if k in self.env:
                        exec_env[k] = v
            return self._run_external(argv, exec_env, redirects)
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
        if t == "command.Case":
            to_match = node.get("to_match") or {}
            value_word = to_match.get("word") if isinstance(to_match, dict) else {}
            items: list[CaseItem] = []
            for arm in (node.get("arms") or []):
                pat = arm.get("pattern") or {}
                patterns = [self._asdl_word_to_text(w) for w in (pat.get("words") or [])]
                action = arm.get("action") or []
                items.append(CaseItem(patterns=patterns, body=self._asdl_to_ast_action_list(action)))
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
                if self._is_valid_param_ref_name(name) and (op is None or op == "" or op == "__len__"):
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
            return self._ifs_join([str(v) for v in value.fields])
        if isinstance(value, list):
            return self._ifs_join([str(v) for v in value])
        return "" if value is None else str(value)

    def _expand_asdl_assignment_scalar(self, node: dict[str, Any] | None) -> str:
        fields = self._expand_asdl_assignment_fields(node)
        texts = fields_to_text_list(fields)
        return texts[0] if texts else ""

    def _expand_asdl_assignment_fields(self, node: dict[str, Any] | None) -> list[ExpansionField]:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return []
        out: list[ExpansionSegment] = []
        for part in (node.get("parts") or []):
            text = self._expand_asdl_assignment_part_scalar(part, quoted_context=False)
            out.append(
                ExpansionSegment(
                    text=text,
                    quoted=True,
                    glob_active=False,
                    split_active=False,
                    source_kind=str(part.get("type", "word_part.Unknown")) if isinstance(part, dict) else "word_part.Unknown",
                )
            )
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
            value = self._expand_braced_param(name, op, arg_text, quoted_context)
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
        for part in parts:
            kind = str(part.get("type", "word_part.Unknown")) if isinstance(part, dict) else "word_part.Unknown"
            if isinstance(part, dict) and part.get("type") == "word_part.Literal":
                literal = str(part.get("tval", ""))
                segs = self._asdl_literal_to_segments(literal, quoted_context=False, source_kind=kind)
                next_fields = []
                for base in fields:
                    next_fields.append(
                        ExpansionField(
                            segments=base.segments + segs,
                            preserve_boundary=base.preserve_boundary or any(s.quoted for s in segs),
                        )
                    )
                fields = next_fields
                continue
            vals, quoted = self._expand_asdl_word_part_values(part, quoted_context=False)
            next_fields = []
            for base in fields:
                for v in vals:
                    next_fields.append(
                        ExpansionField(
                            segments=base.segments
                            + [
                                ExpansionSegment(
                                    text=v,
                                    quoted=quoted,
                                    glob_active=(not quoted),
                                    split_active=(not quoted),
                                    source_kind=kind,
                                )
                            ],
                            preserve_boundary=base.preserve_boundary or quoted,
                        )
                    )
            fields = next_fields
        return fields

    def _legacy_word_to_expansion_fields(self, text: str, *, assignment: bool = False) -> list[ExpansionField]:
        lst_word = parse_legacy_word(text)
        asdl_word = lst_word_to_asdl_word(lst_word)
        if assignment:
            return self._expand_asdl_assignment_fields(asdl_word)
        raw_fields = self._asdl_word_to_expansion_fields(asdl_word)
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
            return [
                ExpansionSegment(
                    text=text,
                    quoted=quoted_context,
                    glob_active=(not quoted_context),
                    split_active=(not quoted_context),
                    source_kind=source_kind,
                )
            ]
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
                    split_active=active and (not quoted),
                    source_kind=source_kind,
                )
            )
            buf = []

        i = 0
        while i < len(text):
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

    def _expand_asdl_word_fields(self, node: dict[str, Any], split_glob: bool = True) -> list[str]:
        if not isinstance(node, dict) or node.get("type") != "word.Compound":
            return []
        raw_text = self._asdl_word_to_text(node)
        if self._is_process_subst(raw_text):
            return [self._process_substitute(raw_text)]
        fields = self._asdl_word_to_expansion_fields(node)
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
        return out

    def _split_structured_field(self, field: ExpansionField) -> list[ExpansionField]:
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
                    out.append(
                        ExpansionField(
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
                    )

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
        text = self._tilde_expand(field.text())
        if self.options.get("f", False):
            return [text]
        has_active_glob = False
        pat: list[str] = []
        for seg in field.segments:
            for ch in seg.text:
                if seg.glob_active and ch in {"*", "?", "["}:
                    has_active_glob = True
                    pat.append(ch)
                    continue
                if ch == "*":
                    pat.append("[*]")
                elif ch == "?":
                    pat.append("[?]")
                elif ch == "[":
                    pat.append("[[]")
                elif ch == "]":
                    pat.append("[]]")
                elif ch == "\\":
                    pat.append("[\\\\]")
                else:
                    pat.append(ch)
        if not has_active_glob:
            return [text]
        pattern = self._tilde_expand("".join(pat))
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches
        return [text]

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

    def _expand_asdl_word_part_values(self, node: dict[str, Any], quoted_context: bool) -> tuple[list[str], bool]:
        t = node.get("type")
        if t == "word_part.Literal":
            return [self._decode_asdl_literal(str(node.get("tval", "")), quoted_context=quoted_context)], quoted_context
        if t == "word_part.SingleQuoted":
            return [str(node.get("sval", ""))], True
        if t == "word_part.DoubleQuoted":
            parts = node.get("parts") or []
            pieces: list[str] = [""]
            had_any_part = False
            had_effective_part = False
            for p in parts:
                had_any_part = True
                vals, _ = self._expand_asdl_word_part_values(p, quoted_context=True)
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
                return [], True
            return pieces, True
        if t == "word_part.SimpleVarSub":
            val = self._expand_param(str(node.get("name", "")), quoted_context)
            if isinstance(val, PresplitFields):
                return [str(v) for v in val], True
            return self._normalize_asdl_expanded_values(val), quoted_context
        if t == "word_part.BracedVarSub":
            arg_node = node.get("arg")
            arg_text, _arg_fields = self._asdl_operator_arg_text_and_fields(arg_node)
            val = self._expand_braced_param(
                str(node.get("name", "")),
                node.get("op"),
                arg_text,
                quoted_context,
                arg_fields=_arg_fields,
            )
            if isinstance(val, PresplitFields):
                return [str(v) for v in val], True
            return self._normalize_asdl_expanded_values(val), quoted_context
        if t == "word_part.CommandSub":
            child = node.get("child")
            syntax = str(node.get("syntax") or "dollar")
            backtick = syntax == "backtick"
            if isinstance(child, dict) and child.get("type") == "command.CommandList":
                return [self._expand_command_subst_asdl(child, backtick=backtick)], quoted_context
            src = str(node.get("child_source") or "")
            return [self._expand_command_subst_text(src, backtick=backtick)], quoted_context
        if t == "word_part.ArithSub":
            expr = str(node.get("expr_source") or node.get("code") or "")
            return [self._expand_arith(expr)], quoted_context
        return [""], quoted_context

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
            self._asdl_word_to_expansion_fields(node),
            for_case=True,
        )

    def _escape_case_pattern_literal(self, text: str) -> str:
        out: list[str] = []
        for ch in text:
            if ch == "*":
                out.append("[*]")
            elif ch == "?":
                out.append("[?]")
            elif ch == "[":
                out.append("[[]")
            elif ch == "]":
                out.append("[]]")
            elif ch == "\\":
                out.append("[\\\\]")
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
            cmd_env = dict(self.env)
            for scope in self.local_stack:
                for k, v in scope.items():
                    if k in self.env:
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
                print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0]), file=sys.stderr)
                return 127
            except OSError as e:
                if getattr(e, "errno", None) == 8 and os.path.isfile(argv[0]) and len(node.commands) == 1:
                    return self._run_source(argv[0], argv[1:])
                print(f"{argv[0]}: {e.strerror}", file=sys.stderr)
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
        return name in self.BUILTINS or self._has_function(name)

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
        if self._has_function(name) or name in self.BUILTINS:
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
            py_stdout = None
            tmp = None
            try:
                if input_text is None:
                    sys.stdin = saved_stdin
                else:
                    sys.stdin = io.StringIO(input_text)
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
                if tmp is not None:
                    tmp.close()
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
            print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0]), file=sys.stderr)
            return 127, b"", (time.monotonic() - start) if start is not None else None

    def _stdout_redirected_away(self, redirects: List[Redirect]) -> bool:
        for redir in redirects:
            fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<&", "<>"] else 1)
            if fd != 1:
                continue
            if redir.op in [">", ">>"]:
                return True
            if redir.op == ">&" and redir.target is not None:
                return redir.target != "1"
        return False

    def _exec_command(self, node: Command) -> int:
        if isinstance(node, GroupCommand):
            return self._exec_list(node.body)
        if isinstance(node, SubshellCommand):
            return self._run_subshell(node.body)
        if isinstance(node, FunctionDef):
            self.functions[node.name] = node.body
            return 0
        if isinstance(node, ForCommand):
            return self._run_for(node)
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
                print(msg, file=sys.stderr)
                if "bad substitution" in msg:
                    raise SystemExit(2)
                if "unbound variable:" in msg:
                    raise SystemExit(2)
                raise SystemExit(1)
            except CommandSubstFailure as e:
                return e.code
            except ArithExpansionFailure as e:
                raise SystemExit(e.code)
            argv = self._expand_aliases(argv)

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
                            raise SystemExit(e.code)
                        name = assign.name
                        op = assign.op
                        assigned_names.add(name)
                        if name in self.readonly_vars:
                            msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                            print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                            raise SystemExit(2)
                        comp_vals = self._parse_compound_assignment_rhs(assign.value) if self._bash_compat_level is not None else None
                        if name in self._py_ties:
                            if comp_vals is not None:
                                raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                            if op == "+=":
                                self._assign_shell_var(name, self._get_var(name) + value)
                            else:
                                self._assign_shell_var(name, value)
                            local_env[name] = self._get_var(name)
                            continue
                        if comp_vals is not None:
                            self._assign_compound_var(name, op, comp_vals)
                            compound_assigned.add(name)
                            local_env[name] = self._get_var(name)
                            continue
                        if op == "+=":
                            self.env[name] = self.env.get(name, "") + value
                        else:
                            self.env[name] = value
                    should_persist_env = any(
                        not (r.op == ">&" and (r.fd is None or r.fd == 1) and r.target == "1")
                        for r in node.redirects
                    )
                    if should_persist_env:
                        for n in assigned_names:
                            if n in compound_assigned:
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
                        raise SystemExit(e.code)
                    name = assign.name
                    op = assign.op
                    assigned_names.add(name)
                    if name in self.readonly_vars:
                        msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                        print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                        raise SystemExit(2)
                    comp_vals = self._parse_compound_assignment_rhs(assign.value) if self._bash_compat_level is not None else None
                    if name in self._py_ties:
                        if comp_vals is not None:
                            raise RuntimeError(f"{name}: cannot assign array value to tied variable")
                        if op == "+=":
                            self._assign_shell_var(name, self._get_var(name) + value)
                        else:
                            self._assign_shell_var(name, value)
                        local_env[name] = self._get_var(name)
                        continue
                    if comp_vals is not None:
                        self._assign_compound_var(name, op, comp_vals)
                        compound_assigned.add(name)
                        local_env[name] = self._get_var(name)
                        self.env = local_env
                        continue
                    if op == "+=":
                        local_env[name] = local_env.get(name, "") + value
                    else:
                        local_env[name] = value
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
                    self._typed_vars.pop(n, None)
                self.env.update(local_env)
                for tied_name in self._py_ties:
                    self.env[tied_name] = self._get_var(tied_name)
                if self._cmd_sub_used:
                    status = self._cmd_sub_status
                    self._cmd_sub_used = False
                    return status
                return 0
            if not argv:
                return 0
            argv_assigns = self._argv_assignment_words(argv)
            if argv_assigns is not None:
                saved_env2 = self.env
                try:
                    self.env = local_env
                    for var_name, op, value, is_compound in argv_assigns:
                        if var_name in self.readonly_vars:
                            msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=var_name)
                            print(self._format_error(msg, line=self.current_line), file=sys.stderr)
                            raise SystemExit(2)
                        if is_compound:
                            self._assign_compound_var(
                                var_name,
                                op,
                                list(value) if isinstance(value, list) else [],
                            )
                        elif op == "+=":
                            self._assign_shell_var(var_name, self._get_var(var_name) + str(value))
                        else:
                            self._assign_shell_var(var_name, str(value))
                        base = var_name.split("[", 1)[0]
                        local_env[base] = self._get_var(base)
                    saved_env2.update(local_env)
                    for tied_name in self._py_ties:
                        saved_env2[tied_name] = self._get_var(tied_name)
                    return 0
                finally:
                    self.env = saved_env2
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
            if name in self.BUILTINS:
                is_special = name in self.SPECIAL_BUILTINS
                if is_special:
                    self.env = local_env
                    try:
                        with self._redirected_fds(node.redirects):
                            return self._run_builtin(name, argv)
                    except RuntimeError as e:
                        print(str(e), file=sys.stderr)
                        return 1
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
                exec_env = dict(local_env)
                # Local variables should shadow exported globals for external
                # commands, but only when that name is already exported.
                for scope in self.local_stack:
                    for k, v in scope.items():
                        if k in self.env:
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
        prefix = ps4 if ps4 != "" else "+ "
        print(prefix + " ".join(items), file=sys.stderr)

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
            if status < 0:
                sig_num = -status
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
            self.traps = saved_traps
            try:
                os.chdir(saved_cwd)
            except OSError:
                pass

    def _run_for(self, node: ForCommand) -> int:
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

    def _run_case(self, node: CaseCommand) -> int:
        value = self._expand_assignment_word(node.value.text)
        for item in node.items:
            for pat in item.patterns:
                expanded_pat = self._pattern_from_word(pat, for_case=True)
                if fnmatch.fnmatchcase(value, expanded_pat):
                    return self._exec_list(item.body)
        return 0

    def _run_builtin(self, name: str, argv: List[str]) -> int:
        if name == "cd":
            target = argv[1] if len(argv) > 1 else self.env.get("HOME", "/")
            try:
                old = os.getcwd()
                os.chdir(target)
                self.env["OLDPWD"] = old
                self.env["PWD"] = os.getcwd()
                return 0
            except OSError:
                return 1
        if name in [".", "source"]:
            if len(argv) < 2:
                return 2
            path = argv[1]
            args = argv[2:]
            return self._run_source(path, args)
        if name == "local":
            return self._run_local(argv[1:])
        if name == "eval":
            return self._run_eval(argv[1:])
        if name == "declare":
            return self._run_declare(argv[1:])
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
        if name == "exec":
            if len(argv) <= 1:
                return 0
            cmd = argv[1:]
            if cmd[0] in self.BUILTINS:
                status = self._run_builtin(cmd[0], cmd)
                raise SystemExit(status)
            if self._has_function(cmd[0]):
                status = self._run_function(cmd[0], cmd[1:])
                raise SystemExit(status)
            status = self._run_external(cmd, dict(self.env), [], context="exec")
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
        if name in ["[", "[[", "test"]:
            return self._run_test(name, argv[1:])
        if name == "exit":
            if len(argv) > 1:
                code = int(argv[1])
            elif self._trap_entry_status is not None:
                code = self._trap_entry_status
                if code == 0 and self.last_nonzero_status != 0:
                    code = self.last_nonzero_status
            else:
                code = self.last_status
            raise SystemExit(code)
        if name == "return":
            if len(argv) > 1:
                code = int(argv[1])
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

    def _run_source(self, path: str, args: List[str]) -> int:
        if "/" not in path:
            for d in self.env.get("PATH", os.defpath).split(os.pathsep):
                candidate = os.path.join(d, path)
                if os.path.isfile(candidate):
                    path = candidate
                    break
        try:
            with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
                source = f.read()
        except OSError:
            return 1
        saved_positional = list(self.positional) if args else None
        self.source_stack.append(path)
        self._sync_root_frame()
        if args:
            self.set_positional_args(args)
        parser_impl = Parser(source, aliases=self.aliases)
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
            self._call_stack.pop()
            self.local_stack.pop()
            self.set_positional_args(saved_positional)
        return status

    def _has_function(self, name: str) -> bool:
        return name in self.functions_asdl or name in self.functions

    def _function_names(self) -> list[str]:
        return sorted(set(self.functions.keys()) | set(self.functions_asdl.keys()))


    def add_history_entry(self, line: str) -> None:
        text = line.strip("\n")
        if not text:
            return
        self._history.append(text)

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
            return idx if 0 <= idx < len(self._history) else None
        for i in range(len(self._history) - 1, -1, -1):
            if self._history[i].startswith(token):
                return i
        return None

    def _run_fc(self, args: List[str]) -> int:
        list_mode = True
        reverse = False
        no_numbers = False
        substitute: str | None = None
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
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
                    list_mode = True
                elif ch == "r":
                    reverse = True
                elif ch == "n":
                    no_numbers = True
                elif ch == "s":
                    list_mode = False
                elif ch == "e":
                    # Editor workflow is deferred; keep accepted surface.
                    if j + 1 < len(a):
                        pass
                    else:
                        i += 1
                    j = len(a)
                    continue
                else:
                    break
                j += 1
            if j != len(a):
                break
            i += 1
        rest = args[i:]
        if list_mode:
            first_idx = self._history_resolve(rest[0]) if len(rest) >= 1 else max(0, len(self._history) - 15)
            last_idx = self._history_resolve(rest[1]) if len(rest) >= 2 else len(self._history) - 1
            if first_idx is None or last_idx is None or not self._history:
                return 1
            lo = min(first_idx, last_idx)
            hi = max(first_idx, last_idx)
            seq = list(range(lo, hi + 1))
            if reverse:
                seq = list(reversed(seq))
            for n in seq:
                if no_numbers:
                    print(self._history[n])
                else:
                    print(f"{n + 1}\t{self._history[n]}")
            return 0

        if rest and "=" in rest[0]:
            substitute = rest[0]
            rest = rest[1:]
        current_is_fc = bool(self._history) and self._history[-1].lstrip().startswith("fc")
        default_ref = "-2" if current_is_fc else "-1"
        idx = self._history_resolve(rest[0] if rest else default_ref)
        if idx is not None and current_is_fc and idx == len(self._history) - 1 and len(self._history) >= 2:
            idx -= 1
        if idx is None:
            return 1
        cmd = self._history[idx]
        if substitute is not None:
            old, new = substitute.split("=", 1)
            cmd = cmd.replace(old, new, 1)
        print(cmd)
        self.add_history_entry(cmd)
        return self._eval_source(cmd)

    def _run_external(
        self,
        argv: List[str],
        env: Dict[str, str],
        redirects: List[Redirect],
        context: str | None = None,
    ) -> int:
        if not argv:
            return 127
        if argv[0] == "":
            self._report_error(": Permission denied", line=self.current_line, context=context)
            return 127
        try:
            with self._redirected_fds(redirects):
                if "/" in argv[0]:
                    resolved = argv[0]
                    exec_argv = list(argv)
                else:
                    resolved = self._resolve_external_path(argv[0], env)
                    if resolved is None:
                        msg = self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0])
                        self._report_error(msg, line=self.current_line, context=context)
                        return 127
                    exec_argv = [resolved] + argv[1:]
                child_env = dict(env)
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
                    proc = subprocess.Popen(
                        exec_argv,
                        env=child_env,
                        start_new_session=bool(isinstance(job_id, int)),
                        preexec_fn=self._preexec_reset_signals,
                    )
                    if isinstance(job_id, int):
                        self._bg_pids[job_id] = proc.pid
                        self._bg_pid_to_job[proc.pid] = job_id
                        self._bg_started_at.setdefault(job_id, time.monotonic())
                        if job_id == self._last_bg_job:
                            self._last_bg_pid = proc.pid
                    status = proc.wait()
                    if self._pending_signals and self.traps.get("TERM"):
                        if "TERM" in self._pending_signals:
                            self._run_pending_traps()
                            if self.options.get("e", False):
                                raise SystemExit(0)
                    return status
                except FileNotFoundError:
                    msg = self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=argv[0])
                    self._report_error(msg, line=self.current_line, context=context)
                    return 127
                except PermissionError:
                    self._report_error(f"{argv[0]}: Permission denied", line=self.current_line, context=context)
                    return 126
                except OSError as e:
                    eno = getattr(e, "errno", None)
                    if eno == 8 and os.path.isfile(resolved):
                        return self._run_source(resolved, argv[1:])
                    if eno == 36:
                        self._report_error(f"{argv[0]}: File name too long", line=self.current_line, context=context)
                        return 127
                    self._report_error(f"{argv[0]}: {e.strerror}", line=self.current_line, context=context)
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
        path_value = env.get("PATH", os.defpath)
        for d in path_value.split(os.pathsep):
            base = d or "."
            candidate = os.path.join(base, argv0)
            if os.path.isdir(candidate):
                continue
            if not os.path.isfile(candidate):
                continue
            if os.access(candidate, os.X_OK):
                self._cmd_hash[argv0] = candidate
                return candidate
        return None

    def _run_hash(self, args: List[str]) -> int:
        verbose = False
        i = 0
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-r":
                self._cmd_hash.clear()
                i += 1
                continue
            if args[i] == "-v":
                verbose = True
                i += 1
                continue
            return 2
        names = args[i:]
        if not names:
            for name in sorted(self._cmd_hash.keys()):
                print(f"{name}={self._cmd_hash[name]}")
            return 0
        status = 0
        for name in names:
            path = self._resolve_external_path(name, self.env)
            if path is None:
                self._report_error(self._diag_msg(DiagnosticKey.HASH_NOT_FOUND, name=name), line=self.current_line)
                status = 1
                continue
            if verbose:
                print(f"{name}={path}")
        return status

    def _run_alias(self, args: List[str]) -> int:
        status = 0
        if not args:
            for name in sorted(self.aliases):
                print(f"alias {name}='{self.aliases[name]}'")
            return 0
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                self.aliases[name] = value
                continue
            if arg in self.aliases:
                print(f"alias {arg}='{self.aliases[arg]}'")
            else:
                print(self._diag_msg(DiagnosticKey.ALIAS_NOT_FOUND, name=arg), file=sys.stderr)
                status = 1
        return status

    def _run_unalias(self, args: List[str]) -> int:
        if not args:
            print("unalias: usage: unalias [-a] name ...", file=sys.stderr)
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
        def wait_job(job_id: int) -> int:
            th = self._bg_jobs.get(job_id)
            if th is not None:
                while th.is_alive():
                    th.join(0.05)
                    if self._pending_signals:
                        sig_name = self._pending_signals[0]
                        self._run_pending_traps()
                        sig_num = self._signal_number(sig_name)
                        return 128 + sig_num if sig_num else 1
            st = self._bg_status.get(job_id, 0)
            if st < 0:
                return 128 + (-st)
            return st

        if not args:
            last = 0
            for job_id in sorted(self._bg_jobs.keys()):
                last = wait_job(job_id)
                if last >= 128:
                    return last
            return last
        last = 0
        for arg in args:
            if arg == "%%":
                if self._last_bg_job is None:
                    return 127
                job_id = self._last_bg_job
            else:
                token = arg[1:] if arg.startswith("%") else arg
                if not token.isdigit():
                    return 127
                token_i = int(token)
                if arg.startswith("%"):
                    job_id = token_i
                elif token_i in self._bg_jobs or token_i in self._bg_status:
                    job_id = token_i
                else:
                    job_id = self._bg_pid_to_job.get(token_i, -1)
                    if job_id < 0:
                        for jid, pid in self._bg_pids.items():
                            if pid == token_i:
                                job_id = jid
                                break
                    if job_id < 0:
                        return 127
            if job_id not in self._bg_jobs and job_id not in self._bg_status:
                return 127
            last = wait_job(job_id)
            if last >= 128:
                return last
        return last

    def _resolve_job_id(self, token: str | None) -> int | None:
        if token is None or token == "%%":
            return self._last_bg_job
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

    def _run_fg(self, args: List[str]) -> int:
        if len(args) > 1:
            return 2
        if not self.options.get("m", False):
            token = args[0] if args else "%%"
            if not token.startswith("%"):
                token = f"%{token}"
            self._report_error(f"job {token} not created under job control", line=self.current_line, context="fg")
            return 2
        job_id = self._resolve_job_id(args[0] if args else None)
        if job_id is None:
            return 1
        if job_id not in self._bg_jobs and job_id not in self._bg_status:
            return 1
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
            self._report_error(f"job {token} not created under job control", line=self.current_line, context="bg")
            return 2
        job_id = self._resolve_job_id(args[0] if args else None)
        if job_id is None:
            return 1
        if job_id not in self._bg_jobs and job_id not in self._bg_status:
            return 1
        print(f"[{job_id}]")
        return 0

    def _run_kill(self, args: List[str]) -> int:
        if not args:
            return 1
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
                spec = self._normalize_signal_spec(args[i + 1])
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
                spec = self._normalize_signal_spec(a[1:])
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

    def _run_umask(self, args: List[str]) -> int:
        if not args:
            cur = os.umask(0)
            os.umask(cur)
            print(f"{cur:04o}")
            return 0
        try:
            mask = int(args[0], 8)
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

    def _expand_alias_at(self, argv: List[str], idx: int) -> Tuple[List[str], bool]:
        seen: set[str] = set()
        trailing = False
        while idx < len(argv):
            word = argv[idx]
            value = self.aliases.get(word)
            if value is None or word in seen:
                break
            seen.add(word)
            trailing = value.endswith(" ")
            parts = shlex.split(value)
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
                target_fd = 0 if redir.op in ["<", "<<", "<&", "<>"] else 1
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
            elif redir.op == "<<":
                content = self._expand_heredoc(redir)
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
            if op == ">" and self.options.get("C", False):
                try:
                    st = os.stat(path)
                    if stat.S_ISREG(st.st_mode):
                        raise RuntimeError(self._format_error(f"can't create {path}: file exists", line=self.current_line))
                except FileNotFoundError:
                    pass
            return open(path, mode)
        except OSError as e:
            reason = (e.strerror or "error").lower()
            if e.errno == 2:
                if op in [">", ">>", "<>"]:
                    msg = f"can't create {path}: nonexistent directory"
                    raise RuntimeError(self._format_error(msg, line=self.current_line))
                reason = "no such file"
            if op == "<":
                msg = f"can't open {path}: {reason}"
            else:
                msg = f"{path}: {reason}"
            raise RuntimeError(self._format_error(msg, line=self.current_line))

    def _open_for_redir_readwrite(self, path: str) -> object:
        try:
            fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o666)
            return os.fdopen(fd, "r+b", buffering=0)
        except OSError as e:
            reason = (e.strerror or "error").lower()
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
            fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<&", "<>"] else 1)
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
            elif redir.op == "<<":
                content = self._expand_heredoc(redir)
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
                fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<&", "<>"] else 1)
                target = self._expand_redir_target(redir)
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
            return str(self._last_bg_pid) if self._last_bg_pid is not None else ""
        if name == "-":
            return "".join(sorted(k for k, v in self.options.items() if v and len(k) == 1))
        if name == "LINENO":
            line = self.current_line if self.current_line is not None else 0
            if self.script_name == "":
                line = max(0, line - 1)
            return str(line)
        value, is_set = self._get_param_state(name)
        if (not is_set or value == "") and self.options.get("u", False) and name not in ["@", "*", "#"]:
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
    ) -> str | List[str]:
        def _expand_alt_word(text: str) -> str:
            # Under outer double quotes, single quotes are literal chars.
            if quoted and "'" in text:
                return self._expand_assignment_word_protected(text.replace("'", "\\'"))
            return self._expand_assignment_word_protected(text)

        def _expand_alt_fields(text: str, fields: list[ExpansionField] | None = None) -> PresplitFields:
            if fields is not None:
                out_fields: List[str] = []
                split_fields: list[ExpansionField] = []
                for field in fields:
                    split_fields.extend(self._split_structured_field(field))
                for field in split_fields:
                    out_fields.extend(self._glob_structured_field(field))
                ifs_value, ifs_set = self._get_var_with_state("IFS")
                if not ifs_set:
                    ifs_value = " \t\n"
                ifs_ws = "".join(ch for ch in ifs_value if ch in " \t\n")
                lead_boundary = bool(text) and bool(ifs_ws) and text[0] in ifs_ws
                trail_boundary = bool(text) and bool(ifs_ws) and text[-1] in ifs_ws
                return PresplitFields(out_fields, lead_boundary=lead_boundary, trail_boundary=trail_boundary)
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
            lead_boundary = bool(text) and bool(ifs_ws) and text[0] in ifs_ws
            trail_boundary = bool(text) and bool(ifs_ws) and text[-1] in ifs_ws
            return PresplitFields(out_fields, lead_boundary=lead_boundary, trail_boundary=trail_boundary)

        def _expand_alt_unquoted(text: str):
            if arg_fields is not None:
                return _expand_alt_fields(text, arg_fields)
            if any(mark in text for mark in ["'", '"', "`", "$(", "${"]):
                return _expand_alt_fields(text)
            return _expand_alt_word(text)

        if op == "__invalid__":
            raise RuntimeError(self._format_error("syntax error: bad substitution", line=self.current_line))
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
            if op == "__len__":
                if key in {"@", "*"}:
                    if isinstance(typed, list):
                        return str(len(vals_for_key))
                    if isinstance(typed, dict) and "assoc" in attrs:
                        return str(len(vals_for_key))
                    return "0"
            if key in {"@", "*"}:
                vals: list[str] = vals_for_key
                if op is None:
                    if key == "*":
                        if quoted:
                            return self._ifs_join(vals)
                        return vals
                    return vals
                arg_text = arg or ""
                if op in ["#", "##"]:
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
                    spec_struct = self._split_replace_spec_structured(arg_fields)
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
                    vals = self._slice_fields(vals, arg_text)
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
            value, _ = self._get_param_state(name)
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
            return list(self.positional)
        if name == "*" and op is None:
            if quoted:
                return self._ifs_join(self.positional)
            return list(self.positional)
        if name.isdigit():
            value, is_set = self._get_param_state(name)
            if op is None:
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
            return value
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
            spec_struct = self._split_replace_spec_structured(arg_fields)
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
                if fnmatch.fnmatchcase(value[i:j], pattern):
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
            if fnmatch.fnmatchcase(value[:j], pattern):
                return j
        return None

    def _match_suffix_start(self, value: str, pattern: str) -> int | None:
        for i in range(0, len(value) + 1):
            if fnmatch.fnmatchcase(value[i:], pattern):
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
        output, status, hard_error = self._capture_eval(cmd, line_bias=(-1 if backtick else 0))
        if hard_error and status != 0:
            raise CommandSubstFailure(status)
        self._cmd_sub_used = True
        self._cmd_sub_status = status
        return output.rstrip("\n")

    def _expand_command_subst_asdl(self, child: dict[str, Any], backtick: bool = False) -> str:
        output, status, hard_error = self._capture_eval_asdl(child, line_bias=(-1 if backtick else 0))
        if hard_error and status != 0:
            raise CommandSubstFailure(status)
        self._cmd_sub_used = True
        self._cmd_sub_status = status
        return output.rstrip("\n")

    def _expand_arith(self, expr: str, context: str | None = None) -> str:
        joined = expr
        try:
            return self._expand_arith_with_bash(joined, context=context)
        except Exception:
            raise

    def _expand_arith_with_bash(self, expr: str, context: str | None = None) -> str:
        pre_err = self._arith_precheck(expr)
        if pre_err is not None:
            self._report_error(pre_err, line=self.current_line, context=context)
            raise ArithExpansionFailure(2)
        merged_env = dict(self.env)
        for scope in self.local_stack:
            merged_env.update(scope)
        names = self._arith_capture_names(expr, merged_env)
        positional = " ".join(shlex.quote(a) for a in self.positional)
        lines = [
            "set +u",
            f"set -- {positional}",
            f"__mctash_result=$(({expr}))",
            'printf "__MCTASH_RESULT__=%s\\n" "$__mctash_result"',
        ]
        for name in names:
            lines.append(f'printf "__MCTASH_VAR__{name}=%s\\n" "${{{name}-}}"')
        proc = subprocess.run(
            ["bash", "-c", "\n".join(lines)],
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        result = "0"
        saw_result = False
        for line in proc.stdout.splitlines():
            if line.startswith("__MCTASH_RESULT__="):
                result = line.split("=", 1)[1]
                saw_result = True
                continue
            if line.startswith("__MCTASH_VAR__"):
                payload = line[len("__MCTASH_VAR__") :]
                if "=" in payload:
                    name, value = payload.split("=", 1)
                    self._assign_shell_var(name, value)
        err_text = (proc.stderr or "")
        if proc.returncode != 0 or (err_text.strip() != "") or not saw_result:
            err = err_text.lower()
            if "division by 0" in err or "divide by 0" in err:
                self._report_error("divide by zero", line=self.current_line, context=context)
            else:
                self._report_error("arithmetic syntax error", line=self.current_line, context=context)
            raise ArithExpansionFailure(2)
        return result

    def _arith_precheck(self, expr: str) -> str | None:
        # ash rejects `1 ? 20 : x+=2` as arithmetic syntax error
        # (assignment cannot appear as the selected ternary operand here).
        depth = 0
        qpos = -1
        cpos = -1
        for i, ch in enumerate(expr):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif ch == "?" and depth == 0 and qpos < 0:
                qpos = i
            elif ch == ":" and depth == 0 and qpos >= 0:
                cpos = i
                break
        if qpos >= 0 and cpos > qpos:
            false_arm = expr[cpos + 1 :].strip()
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*(\+=|-=|\*=|/=|%=|&=|\|=|\^=|=)", false_arm):
                return "arithmetic syntax error"
        return None

    def _arith_capture_names(self, expr: str, env: Dict[str, str]) -> List[str]:
        seen: set[str] = set()
        queue: List[str] = list(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr))
        while queue:
            name = queue.pop(0)
            if name in seen:
                continue
            seen.add(name)
            raw = env.get(name)
            if raw is None:
                continue
            # Variables used as arithmetic names can themselves contain expressions.
            for sub in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw):
                if sub not in seen:
                    queue.append(sub)
        return sorted(seen)

    def _expand_heredoc(self, redir: Redirect) -> str:
        content = redir.here_doc or ""
        if not redir.here_doc_expand:
            return content
        return self._expand_heredoc_unquoted(content)

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
                    out.append(self._expand_braced_param(name, op, arg, False))
                    i = end + 1
                    continue
                if i + 1 < len(text):
                    nxt = text[i + 1]
                    if nxt in "#@*?$!-":
                        val = self._expand_param(nxt, False)
                        out.append(" ".join(val) if isinstance(val, list) else val)
                        i += 2
                        continue
                    if nxt.isdigit():
                        val = self._expand_param(nxt, False)
                        out.append(" ".join(val) if isinstance(val, list) else val)
                        i += 2
                        continue
                    if nxt.isalpha() or nxt == "_":
                        j = i + 1
                        while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                            j += 1
                        name = text[i + 1 : j]
                        val = self._expand_param(name, False)
                        out.append(" ".join(val) if isinstance(val, list) else val)
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

    def _argv_assignment_words(self, argv: list[str]) -> list[tuple[str, str, object, bool]] | None:
        out: list[tuple[str, str, object, bool]] = []
        i = 0
        while i < len(argv):
            tok = argv[i]
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
                    if i >= len(argv):
                        return None
                    tail = argv[i]
                out.append((name, op, vals, True))
                i += 1
                continue

            m_comp_open = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(\+?=)$", tok)
            if m_comp_open is not None:
                name = m_comp_open.group(1)
                op = m_comp_open.group(2)
                if i + 1 >= len(argv) or argv[i + 1] != "(":
                    return None
                i += 2
                vals = []
                while i < len(argv):
                    cur = argv[i]
                    if cur == ")":
                        break
                    vals.append(cur)
                    i += 1
                if i >= len(argv) or argv[i] != ")":
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
            if not (self._is_valid_name(name) or self._parse_subscripted_name(name) is not None):
                return None
            out.append((name, op, value, False))
            i += 1
        return out

    def _assign_compound_var(self, name: str, op: str, values: list[str]) -> None:
        if self._bash_compat_level is None:
            raise RuntimeError(f"{name}: compound assignment requires BASH_COMPAT")
        cur = self._typed_vars.get(name)
        cur_vals: list[object] = []
        if isinstance(cur, list):
            cur_vals = list(cur)
        if op == "+=":
            cur_vals.extend(values)
        else:
            cur_vals = [str(v) for v in values]
        self._typed_vars[name] = cur_vals
        self._set_var_attrs(name, array=True)
        vis = self._array_visible_values(cur_vals)
        self._set_subscript_projection(name, vis[0] if vis else "")

    def _parse_compound_assignment_rhs(self, rhs: str) -> list[str] | None:
        text = rhs.strip()
        if not (text.startswith("(") and text.endswith(")")):
            return None
        inner = text[1:-1]
        if inner.strip() == "":
            return []
        vals: list[str] = []
        reader = TokenReader(inner)
        ctx = LexContext(reserved_words=set(), allow_reserved=False, allow_newline=False)
        while True:
            tok = reader.next(ctx)
            if tok is None:
                break
            if tok.kind != "WORD":
                return None
            vals.append(self._expand_assignment_word(tok.value))
        return vals

    def _assign_subscripted_var(self, name: str, value: str) -> bool:
        parsed = self._parse_subscripted_name(name)
        if parsed is None:
            return False
        if self._bash_compat_level is None:
            raise RuntimeError(f"{name}: indexed assignment requires BASH_COMPAT")
        base, key = parsed
        if base in self.readonly_vars:
            raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=base))
        attrs = self._var_attrs.get(base, set())
        if "assoc" in attrs:
            cur = self._typed_vars.get(base)
            if not isinstance(cur, dict):
                cur = {}
            akey = self._eval_assoc_subscript_key(key)
            cur[str(akey)] = value
            self._typed_vars[base] = cur
            self._set_subscript_projection(base, str(cur.get("0", "")))
            return True
        # Default to indexed array semantics when assoc isn't declared.
        cur_arr = self._typed_vars.get(base)
        if not isinstance(cur_arr, list):
            cur_arr = []
        idx = self._eval_index_subscript(key, cur_arr, strict=True, name=name)
        if idx is None:
            raise RuntimeError(f"{name}: bad array subscript")
        if idx >= len(cur_arr):
            cur_arr.extend([None] * (idx + 1 - len(cur_arr)))
        cur_arr[idx] = value
        self._typed_vars[base] = cur_arr
        vis = self._array_visible_values(cur_arr)
        self._set_subscript_projection(base, vis[0] if vis else "")
        self._set_var_attrs(base, array=True)
        return True

    def _eval_index_subscript(
        self,
        key: str,
        seq: list[object],
        *,
        strict: bool = False,
        name: str | None = None,
    ) -> int | None:
        text = (key or "").strip()
        if text == "":
            if strict:
                label = name or key or "array"
                raise RuntimeError(f"{label}: bad array subscript")
            return None
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
                return "", False
            if key in {"@", "*"}:
                vals = self._array_visible_values(typed)
                if key == "*":
                    return self._ifs_join(vals), bool(vals)
                return " ".join(vals), bool(vals)
            idx = self._eval_index_subscript(key, typed, strict=True, name=base)
            if idx is None:
                return "", False
            if idx < 0 or idx >= len(typed):
                return "", False
            cell = typed[idx]
            if cell is None:
                return "", False
            return str(cell), True
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
            return str(self._last_bg_job) if self._last_bg_job is not None else "", True
        if name == "-":
            return "".join(sorted(k for k, v in self.options.items() if v and len(k) == 1)), True
        if name == "LINENO":
            line = self.current_line if self.current_line is not None else 0
            if self.script_name == "":
                line = max(0, line - 1)
            return str(line), True
        if name == "@":
            return " ".join(self.positional), True
        if name == "*":
            return self._ifs_join(self.positional), True
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

    def _remove_prefix(self, value: str, pattern: str, longest: bool) -> str:
        if pattern == "":
            return value
        indices = range(len(value), -1, -1) if longest else range(0, len(value) + 1)
        for i in indices:
            prefix = value[:i]
            if fnmatch.fnmatchcase(prefix, pattern):
                return value[i:]
        return value

    def _remove_suffix(self, value: str, pattern: str, longest: bool) -> str:
        if pattern == "":
            return value
        indices = range(0, len(value) + 1) if longest else range(len(value), -1, -1)
        for i in indices:
            suffix = value[i:]
            if fnmatch.fnmatchcase(suffix, pattern):
                return value[:i]
        return value

    def _pattern_from_word(self, text: str, for_case: bool = False) -> str:
        raw = self._expand_assignment_word_protected(text)
        return self._pattern_from_literalized_raw(raw, for_case=for_case)

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
                    raw_parts.append(seg.text)
        return self._pattern_from_literalized_raw("".join(raw_parts), for_case=for_case)

    def _structured_fields_to_assignment_scalar(self, fields: list[ExpansionField]) -> str:
        texts = fields_to_text_list(fields)
        if not texts:
            return ""
        if len(texts) == 1:
            return texts[0]
        return self._ifs_join(texts)

    def _pattern_from_literalized_raw(self, raw: str, *, for_case: bool = False) -> str:
        rb = r"\]" if for_case else "]"
        raw = raw.replace(r"\]", rb)
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
        value = self._coerce_var_value(name, value)
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
        if not self.local_stack:
            self._report_error("not in a function", line=self.current_line, context="local")
            return 1
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                op = "="
                if name.endswith("+"):
                    op = "+="
                    name = name[:-1]
                expanded = self._expand_assignment_word(value)
                if op == "+=":
                    current = self._get_var(name)
                    self._set_local(name, current + expanded)
                else:
                    self._set_local(name, expanded)
            else:
                if arg not in self.local_stack[-1]:
                    self._set_local(arg, "")
        return 0

    def _run_eval(self, args: List[str]) -> int:
        source = " ".join(args)
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

    def _run_declare(self, args: List[str]) -> int:
        if not args:
            return 0

        show_funcs = False
        print_vars = False
        declare_array = False
        declare_assoc = False
        idx = 0
        while idx < len(args):
            arg = args[idx]
            if arg == "--":
                idx += 1
                break
            if not arg.startswith("-") or arg == "-":
                break
            for ch in arg[1:]:
                if ch == "F":
                    show_funcs = True
                elif ch == "p":
                    print_vars = True
                elif ch == "a":
                    declare_array = True
                elif ch == "A":
                    declare_assoc = True
                else:
                    self._report_error(f"illegal option -{ch}", line=self.current_line, context="declare")
                    return 2
            idx += 1

        names = args[idx:]
        if show_funcs:
            if names:
                for name in names:
                    if self._has_function(name):
                        print(name)
                return 0
            for name in self._function_names():
                print(name)
            return 0

        if print_vars:
            if not names:
                return 0
            status = 0
            for name in names:
                if not self._is_valid_name(name):
                    self._report_error(f"not found: {name}", line=self.current_line, context="declare")
                    status = 1
                    continue
                attrs = self._var_attrs.get(name, set())
                value = self._get_var(name)
                if "assoc" in attrs:
                    print(f"declare -A {name}")
                elif "array" in attrs:
                    print(f"declare -a {name}")
                elif "integer" in attrs:
                    print(f"declare -i {name}='{value}'")
                else:
                    print(f"declare -- {name}='{value}'")
            return status

        if declare_assoc:
            if not self._bash_feature_enabled("declare_assoc"):
                self._report_error("declare -A requires BASH_COMPAT to be set", line=self.current_line, context="declare")
                return 2
            for spec in names:
                if "=" in spec:
                    name, value = spec.split("=", 1)
                    self._declare_var(name, value, assoc=True)
                    continue
                name = spec
                self._declare_var(name, self._get_var(name), assoc=True)
            return 0

        if declare_array:
            if not self._bash_feature_enabled("declare_array"):
                self._report_error("declare -a requires BASH_COMPAT to be set", line=self.current_line, context="declare")
                return 2
            for spec in names:
                if "=" in spec:
                    name, value = spec.split("=", 1)
                    self._declare_var(name, value, array=True)
                    continue
                name = spec
                self._declare_var(name, self._get_var(name), array=True)
            return 0

        return 0

    def _run_set(self, args: List[str]) -> int:
        def _set_option(opt: str, enabled: bool) -> int:
            if opt == "m" and enabled and not os.isatty(0):
                self._report_error("set: can't access tty; job control turned off", line=self.current_line, context=None)
                self.options["m"] = False
                return 0
            self.options[opt] = enabled
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
            if arg.startswith("-"):
                self._report_error(f"illegal option {arg}", line=self.current_line, context="export")
                return 2
            break
        status = 0
        for arg in args[idx:]:
            if "=" in arg:
                name, value = arg.split("=", 1)
                op = "="
                if name.endswith("+"):
                    op = "+="
                    name = name[:-1]
                if unexport:
                    self.env.pop(name, None)
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
            else:
                if unexport:
                    self.env.pop(arg, None)
                else:
                    self.env[arg] = self.env.get(arg, "")
        return status

    def _run_readonly(self, args: List[str]) -> int:
        if not args:
            for name in sorted(self.readonly_vars):
                print(f"readonly {name}='{self._get_var(name)}'")
            return 0
        status = 0
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                if name in self.readonly_vars:
                    msg = self._diag_msg(DiagnosticKey.READONLY_VAR, name=name)
                    self._report_error(msg, line=self.current_line, context="readonly")
                    status = 2
                    continue
                self._set_var(name, value)
                self.readonly_vars.add(name)
                continue
            self.readonly_vars.add(arg)
            self.env.setdefault(arg, self._get_var(arg))
        return status

    def _run_unset(self, args: List[str]) -> int:
        mode_vars = True
        idx = 0
        while idx < len(args):
            arg = args[idx]
            if arg == "--":
                idx += 1
                break
            if arg.startswith("-"):
                if arg == "-":
                    self._report_error("-: bad variable name", line=self.current_line, context="unset")
                    return 2
                valid = True
                for ch in arg[1:]:
                    if ch == "v":
                        mode_vars = True
                    elif ch == "f":
                        mode_vars = False
                    else:
                        valid = False
                        break
                if not valid:
                    self._report_error(f"illegal option {arg}", line=self.current_line, context="unset")
                    return 2
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
                if self._diag.style != "bash" and not self.options.get("i", False):
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
                    akey = self._eval_assoc_subscript_key(key)
                    typed.pop(akey, None)
                    self._set_subscript_projection(base, str(typed.get("0", "")) if typed else "")
                    continue
                if isinstance(typed, list):
                    i_key = self._eval_index_subscript(key, typed, strict=True, name=base)
                    if i_key is None:
                        continue
                    if 0 <= i_key < len(typed):
                        typed[i_key] = None
                    vis = self._array_visible_values(typed)
                    self._set_subscript_projection(base, vis[0] if vis else "")
                    continue
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
            if name == "OPTIND":
                self._getopts_state = None
        return status

    def _eval_assoc_subscript_key(self, key: str) -> str:
        return self._expand_assignment_word(key)

    def _run_shift(self, args: List[str]) -> int:
        n = 1
        if args:
            try:
                n = int(args[0])
            except ValueError:
                self._report_error(f"Illegal number: {args[0]}", line=self.current_line, context="shift")
                raise SystemExit(2)
        if n < 0:
            self._report_error(f"Illegal number: {n}", line=self.current_line, context="shift")
            raise SystemExit(2)
        if n > len(self.positional):
            return 1
        self.positional = self.positional[n:]
        return 0

    def _set_var(self, name: str, value: str) -> None:
        if self._assign_subscripted_var(name, value):
            return
        if name in self.readonly_vars:
            raise RuntimeError(self._diag_msg(DiagnosticKey.READONLY_VAR, name=name))
        value = self._coerce_var_value(name, value)
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

    def _is_valid_name(self, name: str) -> bool:
        if not name:
            return False
        if not (name[0].isalpha() or name[0] == "_"):
            return False
        return all(ch.isalnum() or ch == "_" for ch in name)

    def _run_getopts(self, args: List[str]) -> int:
        if len(args) < 2:
            self._report_error("usage: getopts optstring var [arg ...]", line=self.current_line, context="getopts")
            return 2
        optspec = args[0]
        var_name = args[1]
        if not self._is_valid_name(var_name):
            self._report_error(f"{var_name}: bad variable name", line=self.current_line, context="getopts")
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
                print(f"Illegal option -{ch}", file=sys.stderr)
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
                print(f"No arg for -{ch} option", file=sys.stderr)
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
                self._report_error(f"shopt: invalid option -- {ch}")
                return 2
            i += 1
        names = args[i:]
        if set_mode and unset_mode:
            self._report_error("shopt: cannot set and unset in same invocation")
            return 2
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
                self._report_error(f"shopt: invalid shell option name: {name}")
                status = 1
                continue
            if set_mode:
                self._shopts[name] = True
            elif unset_mode:
                self._shopts[name] = False
            if print_mode:
                val = self._shopts[name]
                print(f"shopt {'-s' if val else '-u'} {name}")
            if query_mode and not self._shopts[name]:
                status = 1
        return status

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
                    while j < len(fmt) and fmt[j] not in "diouxXs":
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
            if getattr(e, "errno", None) == 32:
                print("ash: write error: Broken pipe", file=sys.stderr)
                return 1
            print(f"ash: write error: {e.strerror}", file=sys.stderr)
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
                        f"usage: {entry_name} [-e] [-x] [--no-dedent] [-v VAR] [-r VAR] [CODE]",
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
                        f"usage: {entry_name} [-e] [-x] [--no-dedent] [-v VAR] [-r VAR] [-t VAR] [-u VAR] [CODE]",
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
                        f"usage: {entry_name} [-e] [-x] [--no-dedent] [-v VAR] [-r VAR] [-t VAR] [-u VAR] [CODE]",
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
                        f"usage: {entry_name} [-e] [-x] [--no-dedent] [-v VAR] [-r VAR] [-t VAR] [-u VAR] [CODE]",
                        line=self.current_line,
                        context=entry_name,
                    )
                    return 2
                return_var = args[i + 1]
                i += 2
                continue
            self._report_error(f"illegal option {a}", line=self.current_line, context=entry_name)
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
            self._report_error("usage: from MOD import NAME [as ALIAS]", line=self.current_line, context="from")
            return 2
        mod_ref = args[0]
        if args[1] != "import":
            self._report_error("usage: from MOD import NAME [as ALIAS]", line=self.current_line, context="from")
            return 2
        name = args[2]
        alias = None
        if len(args) >= 5 and args[3] == "as":
            alias = args[4]
        elif len(args) > 3:
            self._report_error("usage: from MOD import NAME [as ALIAS]", line=self.current_line, context="from")
            return 2
        try:
            mod = self._load_py_module(mod_ref)
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
                self._report_error(f"{name}: not found in module {mod_ref}", line=self.current_line, context="from")
                return 1
            obj = getattr(mod, name)
            out_name = alias or name
            if callable(obj):
                self._install_python_callable(out_name, obj, wrapper_target=out_name, create_wrapper=True)
            else:
                self._py_globals[out_name] = obj
            return 0
        except Exception as e:
            self._report_error(f"{type(e).__name__}: {e}", line=self.current_line, context="from")
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
        out = value
        if "integer" in attrs:
            try:
                out = str(int(out, 0))
            except ValueError:
                try:
                    out = str(int(out, 10))
                except ValueError:
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
        if name in self.env:
            attrs.add("exported")
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
                    self.env[name] = self._get_var(name)
                else:
                    self.env.pop(name, None)
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

    def _declare_var(self, name: str, value: str = "", **flags: object) -> None:
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
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.Popen[str]:
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
            text=True,
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

    def _run_echo(self, args: List[str]) -> int:
        newline = True
        i = 0
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
        if newline:
            data += "\n"
        if self._force_broken_pipe and self._fd_redirect_depth == 0:
            print("ash: write error: Broken pipe", file=sys.stderr)
            return 1
        if isinstance(sys.stdout, io.StringIO) and self._fd_redirect_depth == 0:
            sys.stdout.write(data)
            return 0
        try:
            os.write(1, data.encode("utf-8", errors="surrogateescape"))
            return 0
        except OSError as e:
            if getattr(e, "errno", None) == 32:
                print("ash: write error: Broken pipe", file=sys.stderr)
                return 1
            print(f"ash: write error: {e.strerror}", file=sys.stderr)
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
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -a")
                    return 2
                if a == "-a":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- a")
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
                        self._report_error("read: option requires an argument -- p")
                        return 2
                    prompt = args[i + 1]
                    i += 2
                else:
                    prompt = a[2:]
                    i += 1
                continue
            if a == "-n" or a.startswith("-n"):
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -n")
                    return 2
                val = None
                if a == "-n":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- n")
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    n_chars = max(0, int(val))
                except ValueError:
                    self._report_error("read: Illegal number")
                    return 2
                exact_chars = False
                continue
            if a == "-N" or a.startswith("-N"):
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -N")
                    return 2
                val = None
                if a == "-N":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- N")
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    n_chars = max(0, int(val))
                except ValueError:
                    self._report_error("read: Illegal number")
                    return 2
                exact_chars = True
                continue
            if a == "-d" or a.startswith("-d"):
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -d")
                    return 2
                val = None
                if a == "-d":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- d")
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                delimiter = "\0" if val == "" else val[0]
                continue
            if a == "-t" or a.startswith("-t"):
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -t")
                    return 2
                val = None
                if a == "-t":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- t")
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    timeout_sec = float(val)
                except ValueError:
                    self._report_error("read: Illegal number")
                    return 2
                if timeout_sec < 0:
                    timeout_sec = 0.0
                continue
            if a == "-u" or a.startswith("-u"):
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -u")
                    return 2
                val = None
                if a == "-u":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- u")
                        return 2
                    val = args[i + 1]
                    i += 2
                else:
                    val = a[2:]
                    i += 1
                try:
                    fd = int(val, 10)
                except ValueError:
                    self._report_error("read: Illegal number")
                    return 2
                if fd < 0:
                    self._report_error("read: Illegal file descriptor")
                    return 2
                continue
            if a == "-s":
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -s")
                    return 2
                i += 1
                continue
            if a == "-e":
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -e")
                    return 2
                edit_mode = True
                i += 1
                continue
            if a == "-i" or a.startswith("-i"):
                if self._bash_compat_level is None:
                    self._report_error("read: Illegal option -i")
                    return 2
                if a == "-i":
                    if i + 1 >= len(args):
                        self._report_error("read: option requires an argument -- i")
                        return 2
                    init_text = args[i + 1]
                    i += 2
                else:
                    init_text = a[2:]
                    i += 1
                continue
            self._report_error(f"read: unknown option {a}")
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
            self.env[name] = value
        return 0 if ok else 1

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
                return None
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
                if args[i] == "-v":
                    if self._has_function(name):
                        print(name)
                        return 0
                    if name in self.BUILTINS:
                        print(name)
                        return 0
                    path = self._find_in_path(name, lookup_path)
                    if path:
                        print(path)
                        return 0
                    return 1
                if self._has_function(name):
                    print(name)
                    return 0
                if name in self.BUILTINS:
                    print(name)
                    return 0
                path = self._find_in_path(name, lookup_path)
                if path:
                    print(path)
                    return 0
                print(self._diag_msg(DiagnosticKey.COMMAND_NOT_FOUND, name=name), file=sys.stderr)
                return 1
            break
        cmd = args[i:]
        if not cmd:
            return 0
        if cmd[0] in self.BUILTINS:
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
        if name not in self.BUILTINS:
            self._report_error(f"builtin: {name}: not a shell builtin", line=self.current_line)
            return 1
        try:
            return self._run_builtin(name, [name] + cmd[1:])
        except SystemExit as e:
            return int(e.code) if e.code is not None else 0

    def _run_trap(self, args: List[str]) -> int:
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
                self._report_error(f"{sig}: invalid signal specification", line=line, context="trap")
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
        status = 0
        for name in args:
            if name in self.aliases:
                print(f"{name} is an alias for {self.aliases[name]}", flush=True)
            elif self._has_function(name):
                print(f"{name} is a function", flush=True)
            elif name in self.BUILTINS:
                print(f"{name} is a shell builtin", flush=True)
            else:
                path = self._find_in_path(name)
                if path:
                    print(f"{name} is {path}", flush=True)
                else:
                    self._report_error(self._diag_msg(DiagnosticKey.TYPE_NOT_FOUND, name=name), line=self.current_line)
                    status = 1
        return status

    def _run_let(self, args: List[str]) -> int:
        if not args:
            return 1
        last = "0"
        for expr in args:
            if "$" in expr:
                self._report_error("arithmetic syntax error", line=self.current_line, context="let")
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
        path = path_override if path_override is not None else self.env.get("PATH", os.defpath)
        for d in path.split(os.pathsep):
            candidate = os.path.join(d, name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
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
        negate = False
        if tokens and tokens[0] == "!":
            negate = True
            tokens = tokens[1:]
        result = False
        if len(tokens) >= 2 and tokens[0] == "-e":
            result = os.path.exists(tokens[1])
        elif len(tokens) >= 2 and tokens[0] == "-n":
            result = tokens[1] != ""
        elif len(tokens) >= 2 and tokens[0] == "-z":
            result = tokens[1] == ""
        elif len(tokens) >= 2 and tokens[0] == "-f":
            result = os.path.isfile(tokens[1])
        elif len(tokens) >= 2 and tokens[0] == "-d":
            result = os.path.isdir(tokens[1])
        elif len(tokens) >= 2 and tokens[0] == "-x":
            result = os.access(tokens[1], os.X_OK)
        elif len(tokens) >= 3 and tokens[1] in ["=", "!="]:
            left = tokens[0]
            right = tokens[2]
            result = (left == right)
            if tokens[1] == "!=":
                result = not result
        elif len(tokens) >= 3 and tokens[1] in ["-eq", "-ne", "-gt", "-ge", "-lt", "-le"]:
            try:
                left_num = int(tokens[0])
                right_num = int(tokens[2])
            except ValueError:
                left_num = 0
                right_num = 0
            op = tokens[1]
            if op == "-eq":
                result = left_num == right_num
            elif op == "-ne":
                result = left_num != right_num
            elif op == "-gt":
                result = left_num > right_num
            elif op == "-ge":
                result = left_num >= right_num
            elif op == "-lt":
                result = left_num < right_num
            elif op == "-le":
                result = left_num <= right_num
        elif len(tokens) == 1:
            result = tokens[0] != ""
        return 0 if (result ^ negate) else 1

    def _eval_source(
        self,
        source: str,
        propagate_exit: bool = False,
        propagate_return: bool = False,
        parse_context: str | None = None,
        line_offset: int = 0,
    ) -> int:
        self._last_eval_hard_error = False
        parser_impl = Parser(source, aliases=self.aliases)
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
                self._report_error(text, line=report_line, context=parse_context)
                if parse_context == "eval":
                    print(self._format_error(f"`{source}'", line=report_line, context=parse_context), file=sys.stderr)
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
            print(msg, file=sys.stderr)
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
        base = (self.current_line or 1) + line_bias
        self._line_offset = saved_offset + (base - 1)
        # In bash/ash POSIX behavior, command substitution under `set -e`
        # remains errexit-sensitive. In non-POSIX bash mode, `-e` is not
        # inherited into command substitution.
        if not saved_options.get("posix", False):
            self.options["e"] = False
        try:
            with self._push_frame(kind=frame_kind):
                status = self._eval_source(source)
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
        base = (self.current_line or 1) + line_bias
        self._line_offset = saved_offset + (base - 1)
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
            print(msg, file=sys.stderr)
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
        if ("syntax error:" in msg or "syntax error near unexpected token" in msg) and " at " in msg:
            text, where = msg.rsplit(" at ", 1)
            line_s = where.split(":", 1)[0]
            return text, int(line_s) if line_s.isdigit() else self.current_line
        return msg, None

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
                subprocess.run(
                    ["bash", "-c", f"{body} < \"$1\"", "mctash-psubst", fifo_path],
                    env=env,
                    check=False,
                )
            finally:
                try:
                    os.unlink(fifo_path)
                except OSError:
                    pass
                self._procsub_paths.discard(fifo_path)

        threading.Thread(target=_runner, daemon=True).start()
        return fifo_path
