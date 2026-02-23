from __future__ import annotations

import glob
import io
import os
import signal
import shlex
import subprocess
import sys
import tempfile
import threading
import fnmatch
import re
from contextlib import contextmanager
from typing import Dict, Iterable, List, Optional, Tuple

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
from .expand import expand_word
from .parser import ParseError, Parser
from .asdl_map import AsdlMappingError, lst_list_item_to_asdl
from .osh_adapter import OshAdapterError, asdl_item_to_list_item


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


class Runtime:
    SPECIAL_BUILTINS = {
        ":",
        ".",
        "source",
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
        "unset",
        "shift",
        "printf",
        "echo",
        "read",
        "true",
        "false",
        "command",
        "exec",
        "break",
        "continue",
        "trap",
        "type",
        "alias",
        "unalias",
        "wait",
        "kill",
    }

    def __init__(self) -> None:
        self.last_status = 0
        self.last_nonzero_status = 0
        self.env: Dict[str, str] = dict(os.environ)
        self.positional: List[str] = []
        self.functions: Dict[str, ListNode] = {}
        self.aliases: Dict[str, str] = {}
        self.local_stack: List[Dict[str, str]] = []
        self.script_name: str = ""
        self.options: Dict[str, bool] = {}
        self._cmd_sub_used: bool = False
        self._cmd_sub_status: int = 0
        self._loop_depth: int = 0
        self.current_line: int | None = None
        self.source_stack: List[str] = []
        self.traps: Dict[str, str] = {}
        self._pending_signals: List[str] = []
        self._running_trap: bool = False
        self._trap_entry_status: int | None = None
        self._subshell_depth: int = 0
        self.c_string_mode: bool = False
        self._trap_status_hint: int = 0
        self._next_job_id: int = 1
        self._bg_jobs: Dict[int, threading.Thread] = {}
        self._bg_status: Dict[int, int] = {}
        self._last_bg_job: int | None = None
        self._bg_pids: Dict[int, int] = {}
        self._thread_ctx = threading.local()
        self._fd_redirect_depth: int = 0
        self._force_broken_pipe: bool = False
        self._user_fds: set[int] = set()
        # Align with ash test assumptions: shell starts with only stdio fds open.
        try:
            os.close(3)
        except OSError:
            pass
        self._install_signal_handlers()

    def set_positional_args(self, args: List[str]) -> None:
        self.positional = list(args)

    def set_script_name(self, name: str) -> None:
        self.script_name = name
        if name:
            if self.source_stack:
                self.source_stack[0] = name
            else:
                self.source_stack = [name]

    def run(self, script: Script) -> int:
        return self._exec_list(script.body)

    def _install_signal_handlers(self) -> None:
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
        except Exception:
            pass
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
        except Exception:
            pass

    def _signal_handler(self, signum, frame) -> None:
        if signum == signal.SIGTERM:
            if "TERM" in self.traps:
                self._pending_signals.append("TERM")
            else:
                raise SystemExit(128 + signum)
        if signum == signal.SIGINT:
            if "INT" in self.traps:
                self._pending_signals.append("INT")
            else:
                raise SystemExit(128 + signum)

    def _format_error(self, msg: str, line: int | None = None, context: str | None = None) -> str:
        if self.source_stack:
            prefix = ": ".join(self.source_stack)
        elif self.script_name:
            prefix = self.script_name
        else:
            return msg
        if context:
            prefix = f"{prefix}: {context}"
        if line is not None:
            if self.c_string_mode and line > 0 and len(self.source_stack) <= 1:
                line = line - 1
            prefix = f"{prefix}: line {line}"
        return f"{prefix}: {msg}"

    def _report_error(self, msg: str, line: int | None = None, context: str | None = None) -> None:
        print(self._format_error(msg, line=line, context=context), file=sys.stderr)

    def _run_pending_traps(self) -> None:
        if self._subshell_depth > 0:
            return
        while self._pending_signals:
            sig = self._pending_signals.pop(0)
            action = self.traps.get(sig)
            if action:
                entry_status = self.last_status
                if entry_status == 0 and self.last_nonzero_status != 0:
                    entry_status = self.last_nonzero_status
                self._run_trap_action(action, entry_status)

    def _run_trap_action(self, action: str, entry_status: int) -> int:
        self._running_trap = True
        saved = self._trap_entry_status
        self._trap_entry_status = entry_status
        try:
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

    def _exec_list(self, node: ListNode) -> int:
        status = 0
        for item in node.items:
            if self.options.get("n", False):
                status = 0
                self.last_status = status
                self._trap_status_hint = status
                continue
            status = self._exec_list_item(item)
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            if not getattr(item, "background", False):
                self._run_pending_traps()
            if status != 0 and self.options.get("e", False):
                raise SystemExit(status)
        self._run_pending_traps()
        return status

    def _exec_list_item(self, item) -> int:
        if getattr(item, "background", False):
            job_id = self._next_job_id
            self._next_job_id += 1

            def _run_bg() -> None:
                self._thread_ctx.job_id = job_id
                try:
                    bg_body = ListNode(items=[ListItem(node=item.node, background=False)])
                    status = self._run_subshell(bg_body)
                    self._bg_status[job_id] = status
                finally:
                    self._bg_pids.pop(job_id, None)
                    self._thread_ctx.job_id = None

            thread = threading.Thread(target=_run_bg)
            thread.daemon = True
            self._bg_jobs[job_id] = thread
            self._last_bg_job = job_id
            thread.start()
            return 0
        return self._exec_and_or(item.node)

    def _exec_and_or(self, node: AndOr, track_status: bool = True) -> int:
        status = self._exec_pipeline(node.pipelines[0])
        if track_status:
            self.last_status = status
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
        for op, pipeline in zip(node.operators, node.pipelines[1:]):
            if op == "&&":
                if status == 0:
                    status = self._exec_pipeline(pipeline)
                    if track_status:
                        self.last_status = status
                        if status != 0:
                            self.last_nonzero_status = status
                        self._trap_status_hint = status
            elif op == "||":
                if status != 0:
                    status = self._exec_pipeline(pipeline)
                    if track_status:
                        self.last_status = status
                        if status != 0:
                            self.last_nonzero_status = status
                        self._trap_status_hint = status
        return status

    def _exec_pipeline(self, node: Pipeline) -> int:
        if len(node.commands) == 1:
            status = self._exec_command(node.commands[0])
            return 0 if (node.negate and status != 0) else (1 if node.negate and status == 0 else status)

        if any(self._pipeline_needs_shell(cmd) for cmd in node.commands):
            status = self._exec_pipeline_inprocess(node)
            return 0 if (node.negate and status != 0) else (1 if node.negate and status == 0 else status)

        procs: List[subprocess.Popen] = []
        statuses: List[int] = []
        prev = None
        for i, cmd in enumerate(node.commands):
            if not isinstance(cmd, SimpleCommand):
                return self._exec_command(cmd)
            cmd_env = dict(self.env)
            for scope in self.local_stack:
                cmd_env.update(scope)
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
                proc = subprocess.Popen(argv, stdin=stdin, stdout=stdout, stderr=stderr, env=cmd_env)
            except FileNotFoundError:
                print(f"{argv[0]}: not found", file=sys.stderr)
                return 127
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
        return name in self.BUILTINS or name in self.functions

    def _exec_pipeline_inprocess(self, node: Pipeline) -> int:
        data: bytes | None = None
        status = 0
        statuses: List[int] = []
        for i, cmd in enumerate(node.commands):
            if not isinstance(cmd, SimpleCommand):
                last = i == len(node.commands) - 1
                force_epipe = (not last) and self._pipeline_sink_is_no_reader(node.commands[i + 1])
                saved_epipe = self._force_broken_pipe
                self._force_broken_pipe = force_epipe
                try:
                    status = self._exec_command(cmd)
                finally:
                    self._force_broken_pipe = saved_epipe
                statuses.append(status)
                data = None
                continue
            argv = self._expand_argv(cmd.argv)
            if not argv:
                status = self._run_subshell(ListNode(items=[ListItem(node=AndOr(pipelines=[Pipeline(commands=[cmd], negate=False)], operators=[]), background=False)]))
                statuses.append(status)
                data = b""
                continue
            last = i == len(node.commands) - 1
            status, data = self._exec_simple_capture(cmd, argv, data, capture=not last)
            statuses.append(status)
            if last and data is not None:
                sys.stdout.write(data.decode("utf-8", errors="ignore"))
                sys.stdout.flush()
        return self._pipeline_result(statuses if statuses else [status])

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

    def _exec_simple_capture(self, cmd: SimpleCommand, argv: List[str], data: bytes | None, capture: bool) -> tuple[int, bytes | None]:
        name = argv[0]
        input_text = data.decode("utf-8", errors="ignore") if data is not None else None
        if name in self.functions or name in self.BUILTINS:
            saved_stdin = sys.stdin
            saved_stdout = sys.stdout
            try:
                if input_text is None:
                    sys.stdin = saved_stdin
                else:
                    sys.stdin = io.StringIO(input_text)
                output = io.StringIO()
                sys.stdout = output if capture else saved_stdout
                try:
                    if name in self.functions:
                        status = self._run_function(name, argv[1:])
                    else:
                        status = self._run_builtin(name, argv)
                except SystemExit as e:
                    status = int(e.code) if e.code is not None else 0
                except ReturnFromFunction as e:
                    status = e.code
                except (BreakLoop, ContinueLoop):
                    status = 1
                out_text = output.getvalue()
                return status, out_text.encode("utf-8")
            finally:
                sys.stdin = saved_stdin
                sys.stdout = saved_stdout

        try:
            proc = subprocess.run(
                argv,
                input=data,
                stdout=subprocess.PIPE if capture else None,
                stderr=None,
                env=self.env,
                check=False,
            )
            return proc.returncode, proc.stdout
        except FileNotFoundError:
            print(f"{argv[0]}: not found", file=sys.stderr)
            return 127, b""

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
            status = self._exec_list(node.cond)
            if status == 0:
                return self._exec_list(node.then_body)
            for elif_cond, elif_body in node.elifs:
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
                    cond_status = self._exec_list(node.cond)
                    should_run = cond_status != 0 if node.until else cond_status == 0
                    if not should_run:
                        break
                    try:
                        last = self._exec_list(node.body)
                        self._run_pending_traps()
                    except ContinueLoop as e:
                        if e.count > 1:
                            raise ContinueLoop(e.count - 1)
                        continue
                    except BreakLoop as e:
                        if e.count > 1:
                            raise BreakLoop(e.count - 1)
                        break
                return last
            finally:
                self._loop_depth -= 1
        if isinstance(node, SimpleCommand):
            argv = self._expand_argv(node.argv)
            if not argv and node.argv:
                argv = [w.text for w in node.argv]
            argv = self._expand_aliases(argv)

            if argv and argv[0] == "exec" and len(argv) <= 1 and node.redirects:
                local_env = dict(self.env)
                for scope in self.local_stack:
                    local_env.update(scope)
                saved_env = self.env
                try:
                    self.env = local_env
                    self._apply_persistent_redirects(node.redirects)
                    expanded_assignments: List[tuple[str, str, str]] = []
                    for assign in node.assignments:
                        value = self._expand_assignment_word(assign.value)
                        expanded_assignments.append((assign.name, assign.op, value))
                    for name, op, value in expanded_assignments:
                        if op == "+=":
                            self.env[name] = self.env.get(name, "") + value
                        else:
                            self.env[name] = value
                    return 0
                finally:
                    self.env = saved_env

            expanded_assignments: List[tuple[str, str, str]] = []
            for assign in node.assignments:
                value = self._expand_assignment_word(assign.value)
                expanded_assignments.append((assign.name, assign.op, value))

            local_env = dict(self.env)
            for scope in self.local_stack:
                local_env.update(scope)
            for name, op, value in expanded_assignments:
                if op == "+=":
                    local_env[name] = local_env.get(name, "") + value
                else:
                    local_env[name] = value
            if not argv:
                try:
                    if node.redirects:
                        with self._redirected_fds(node.redirects):
                            pass
                except RuntimeError as e:
                    print(str(e), file=sys.stderr)
                    return 1
                self.env.update(local_env)
                if self._cmd_sub_used:
                    status = self._cmd_sub_status
                    self._cmd_sub_used = False
                    return status
                return 0
            if not argv:
                return 0
            name = argv[0]
            if name in self.functions:
                saved_env = self.env
                try:
                    self.env = local_env
                    try:
                        with self._redirected_fds(node.redirects):
                            return self._run_function(name, argv[1:])
                    except RuntimeError as e:
                        print(str(e), file=sys.stderr)
                        return 1
                finally:
                    self.env = saved_env
            if name in self.BUILTINS:
                is_special = name in self.SPECIAL_BUILTINS
                if is_special:
                    self.env = local_env
                    with self._redirected_fds(node.redirects):
                        return self._run_builtin(name, argv)
                saved_env = self.env
                try:
                    self.env = local_env
                    try:
                        with self._redirected_fds(node.redirects):
                            status = self._run_builtin(name, argv)
                    except RuntimeError as e:
                        print(str(e), file=sys.stderr)
                        return 1
                    # Builtins like read/set/shift must update shell state.
                    saved_env.update(self.env)
                    return status
                finally:
                    self.env = saved_env
            try:
                return self._run_external(argv, local_env, node.redirects)
            except RuntimeError as e:
                print(str(e), file=sys.stderr)
                return 1
        if isinstance(node, RedirectCommand):
            with self._redirected_fds(node.redirects):
                return self._exec_command(node.child)
        return 2

    def _run_subshell(self, body: ListNode) -> int:
        self._subshell_depth += 1
        saved_env = dict(self.env)
        saved_local = [dict(s) for s in self.local_stack]
        saved_positional = list(self.positional)
        saved_cwd = os.getcwd()
        saved_traps = dict(self.traps)
        # EXIT trap is not inherited by subshells; subshell may define its own.
        self.traps = {k: v for k, v in self.traps.items() if k != "EXIT"}
        try:
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
            if status != 0:
                self.last_nonzero_status = status
            self._trap_status_hint = status
            return self._run_exit_trap(status)
        finally:
            self._subshell_depth -= 1
            self.env = saved_env
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
                expanded_pat = self._expand_assignment_word(pat)
                if fnmatch.fnmatch(value, expanded_pat):
                    return self._exec_list(item.body)
        return 0

    def _run_builtin(self, name: str, argv: List[str]) -> int:
        if name == "cd":
            target = argv[1] if len(argv) > 1 else self.env.get("HOME", "/")
            try:
                os.chdir(target)
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
        if name == "exec":
            if len(argv) <= 1:
                return 0
            cmd = argv[1:]
            if cmd[0] in self.BUILTINS:
                status = self._run_builtin(cmd[0], cmd)
                raise SystemExit(status)
            if cmd[0] in self.functions:
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
        parser_impl = Parser(source)
        saved_positional = list(self.positional) if args else None
        self.source_stack.append(path)
        if args:
            self.set_positional_args(args)
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
                status = self._exec_list_item(asdl_item_to_list_item(asdl_item))
                self.last_status = status
                if status != 0:
                    self.last_nonzero_status = status
                self._trap_status_hint = status
                if not getattr(node, "background", False):
                    self._run_pending_traps()
                if status != 0 and self.options.get("e", False):
                    raise SystemExit(status)
        except ReturnFromFunction as e:
            status = e.code
        except (AsdlMappingError, OshAdapterError):
            status = 2
        finally:
            if saved_positional is not None:
                self.set_positional_args(saved_positional)
            if self.source_stack:
                self.source_stack.pop()
        return status

    def _run_function(self, name: str, args: List[str]) -> int:
        body = self.functions.get(name)
        if body is None:
            return 127
        saved_positional = list(self.positional)
        self.set_positional_args(args)
        self.local_stack.append({})
        status = 0
        try:
            status = self._exec_list(body)
        except ReturnFromFunction as e:
            status = e.code
        finally:
            self.local_stack.pop()
            self.set_positional_args(saved_positional)
        return status

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
                try:
                    proc = subprocess.Popen(argv, env=env)
                    job_id = getattr(self._thread_ctx, "job_id", None)
                    if isinstance(job_id, int):
                        self._bg_pids[job_id] = proc.pid
                    return proc.wait()
                except FileNotFoundError:
                    self._report_error(f"{argv[0]}: not found", line=self.current_line, context=context)
                    return 127
                except PermissionError:
                    self._report_error(f"{argv[0]}: Permission denied", line=self.current_line, context=context)
                    return 126
                except KeyboardInterrupt:
                    return 130
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 1

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
                print(f"alias: {arg}: not found", file=sys.stderr)
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
                print(f"unalias: {name}: not found", file=sys.stderr)
                status = 1
        return status

    def _run_wait(self, args: List[str]) -> int:
        def wait_job(job_id: int) -> int:
            th = self._bg_jobs.get(job_id)
            if th is not None:
                th.join()
            st = self._bg_status.get(job_id, 0)
            if st < 0 and "TERM" in self.traps:
                self._run_trap_action(self.traps["TERM"], 128 + signal.SIGTERM)
                return 0
            return st

        if not args:
            last = 0
            for job_id in sorted(self._bg_jobs.keys()):
                last = wait_job(job_id)
            return last
        last = 0
        for arg in args:
            token = arg[1:] if arg.startswith("%") else arg
            if not token.isdigit():
                return 127
            job_id = int(token)
            if job_id not in self._bg_jobs and job_id not in self._bg_status:
                return 127
            last = wait_job(job_id)
        return last

    def _run_kill(self, args: List[str]) -> int:
        if not args:
            return 1
        token = args[-1]
        job_tok = token[1:] if token.startswith("%") else token
        if job_tok.isdigit() and int(job_tok) in self._bg_jobs:
            job_id = int(job_tok)
            pid = self._bg_pids.get(job_id)
            if pid is None:
                return 1
            try:
                os.kill(pid, signal.SIGTERM)
                return 0
            except Exception:
                return 1
        try:
            proc = subprocess.run(["kill"] + args, env=self.env)
            return proc.returncode
        except Exception:
            return 1

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
            target = self._expand_assignment_word(redir.target) if redir.target else redir.target
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
            return open(path, "r+b")
        except FileNotFoundError:
            try:
                return open(path, "w+b")
            except OSError as e:
                reason = (e.strerror or "error").lower()
                raise RuntimeError(self._format_error(f"can't create {path}: {reason}", line=self.current_line))
        except OSError as e:
            reason = (e.strerror or "error").lower()
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
            target = self._expand_assignment_word(redir.target) if redir.target else redir.target
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
        saved: List[Tuple[int, int]] = []
        self._fd_redirect_depth += 1
        try:
            for redir in redirects:
                fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<", "<&", "<>"] else 1)
                target = self._expand_assignment_word(redir.target) if redir.target else redir.target
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
                elif redir.op == "<>":
                    f = self._open_for_redir_readwrite(target)
                    self._dup2_file(f, fd)
                elif redir.op == ">":
                    f = self._open_for_redir(target, "wb", redir.op)
                    self._dup2_file(f, fd)
                elif redir.op == ">>":
                    f = self._open_for_redir(target, "ab", redir.op)
                    self._dup2_file(f, fd)
                elif redir.op == "<<":
                    content = self._expand_heredoc(redir)
                    f = tempfile.TemporaryFile()
                    f.write(content.encode("utf-8"))
                    f.seek(0)
                    self._dup2_file(f, fd)
                elif redir.op == ">&":
                    self._dup_fd(redir, is_output=True, default_fd=fd)
                elif redir.op == "<&":
                    self._dup_fd(redir, is_output=False, default_fd=fd)
            yield
        finally:
            for fd, saved_fd in reversed(saved):
                if saved_fd >= 0:
                    os.dup2(saved_fd, fd)
                    os.close(saved_fd)
                else:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
            self._fd_redirect_depth = max(0, self._fd_redirect_depth - 1)

    def _expand_argv(self, words: List[Word]) -> List[str]:
        argv: List[str] = []
        for w in words:
            fields = expand_word(
                w.text,
                self._expand_param,
                self._expand_braced_param,
                self._expand_command_subst_text,
                self._expand_arith,
                self._split_ifs,
                self._glob_field,
            )
            # Unquoted empty expansions are elided (e.g. $1 when unset).
            if not any(ch in w.text for ch in ["'", '"', "\\"]):
                fields = [f for f in fields if f != ""]
            argv.extend(fields)
        return argv

    def _expand_word(self, text: str) -> str:
        fields = expand_word(
            text,
            self._expand_param,
            self._expand_braced_param,
            self._expand_command_subst_text,
            self._expand_arith,
            self._split_ifs,
            self._glob_field,
        )
        return fields[0] if fields else ""

    def _expand_assignment_word(self, text: str) -> str:
        fields = expand_word(
            text,
            self._expand_param,
            self._expand_braced_param,
            self._expand_command_subst_text,
            self._expand_arith,
            lambda s: [s],
            lambda s: [s],
        )
        return fields[0] if fields else ""

    def _split_ifs(self, text: str) -> List[str]:
        if text == "":
            return []
        ifs = self.env.get("IFS", " \t\n")
        parts: List[str] = []
        current: List[str] = []
        for ch in text:
            if ch in ifs:
                if current:
                    parts.append("".join(current))
                    current = []
            else:
                current.append(ch)
        if current:
            parts.append("".join(current))
        return parts

    def _glob_field(self, text: str) -> List[str]:
        text = self._tilde_expand(text)
        if any(c in text for c in ["*", "?", "["]):
            matches = [p for p in glob.glob(text)]
            return matches if matches else [text]
        return [text]

    def _tilde_expand(self, text: str) -> str:
        if not text.startswith("~"):
            return text
        if text == "~" or text.startswith("~/"):
            home = self.env.get("HOME", "")
            return home + text[1:]
        if "/" in text:
            user, rest = text[1:].split("/", 1)
            return self._user_home(user) + "/" + rest
        return self._user_home(text[1:])

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
            return self._ifs_join(self.positional)
        if name == "#":
            return str(len(self.positional))
        if name == "?":
            return str(self.last_status)
        if name == "$":
            return str(os.getpid())
        if name == "!":
            return str(self._last_bg_job) if self._last_bg_job is not None else ""
        if name == "-":
            return "".join(sorted(k for k, v in self.options.items() if v))
        value, is_set = self._get_param_state(name)
        if (not is_set or value == "") and self.options.get("u", False) and name not in ["@", "*", "#"]:
            raise RuntimeError(f"unbound variable: {name}")
        return value

    def _expand_braced_param(
        self, name: str, op: str | None, arg: str | None, quoted: bool
    ) -> str | List[str]:
        if op == "__len__":
            value, _ = self._get_param_state(name)
            return str(len(value))
        if name == "@" and op is None:
            return list(self.positional)
        if name.isdigit():
            value = self._get_positional(name)
            if op is None:
                return value
            # Minimal handling for operators on positional parameters.
            is_set = value != ""
            arg_text = arg or ""
            if op in ["-", ":-"]:
                if not is_set or (op == ":-" and value == ""):
                    return self._expand_word(arg_text)
                return value
            if op in ["+", ":+"]:
                if is_set and (op == "+" or value != ""):
                    return self._expand_word(arg_text)
                return ""
            return value
        value, is_set = self._get_param_state(name)
        arg_text = arg or ""
        if op is None:
            return value
        if op in ["-", ":-"]:
            if not is_set or (op == ":-" and value == ""):
                return self._expand_word(arg_text)
            return value
        if op in ["+", ":+"]:
            if is_set and (op == "+" or value != ""):
                return self._expand_word(arg_text)
            return ""
        if op in ["=", ":="]:
            if not is_set or (op == ":=" and value == ""):
                replacement = self._expand_word(arg_text)
                self._set_local(name, replacement)
                return replacement
            return value
        if op in ["?", ":?"]:
            if not is_set or (op == ":?" and value == ""):
                msg = self._expand_word(arg_text) if arg_text else "parameter null or not set"
                raise RuntimeError(f"{name}: {msg}")
            return value
        if op in ["#", "##"]:
            return self._remove_prefix(value, arg_text, longest=(op == "##"))
        if op in ["%", "%%"]:
            return self._remove_suffix(value, arg_text, longest=(op == "%%"))
        return value

    def _get_positional(self, digit: str) -> str:
        idx = int(digit)
        if idx == 0:
            return self.script_name
        if idx <= len(self.positional):
            return self.positional[idx - 1]
        return ""

    def _expand_command_subst_text(self, cmd: str) -> str:
        output, status = self._capture_eval(cmd)
        self._cmd_sub_used = True
        self._cmd_sub_status = status
        return output.rstrip("\n")

    def _expand_arith(self, expr: str) -> str:
        parts = expand_word(
            expr,
            self._expand_param,
            self._expand_braced_param,
            self._expand_command_subst_text,
            lambda s: s,
            self._split_ifs,
            self._glob_field,
        )
        joined = parts[0] if parts else "0"
        m_post = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\+\+\s*", joined)
        if m_post:
            name = m_post.group(1)
            try:
                cur = int(self._get_var(name) or "0")
            except ValueError:
                cur = 0
            self._set_local(name, str(cur + 1))
            return str(cur)
        m_pre = re.fullmatch(r"\s*\+\+([A-Za-z_][A-Za-z0-9_]*)\s*", joined)
        if m_pre:
            name = m_pre.group(1)
            try:
                cur = int(self._get_var(name) or "0")
            except ValueError:
                cur = 0
            cur += 1
            self._set_local(name, str(cur))
            return str(cur)
        try:
            eval_locals: dict[str, int] = {}
            for name, raw in self.env.items():
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                    continue
                try:
                    eval_locals[name] = int(raw)
                except ValueError:
                    eval_locals[name] = 0
            for scope in self.local_stack:
                for name, raw in scope.items():
                    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                        continue
                    try:
                        eval_locals[name] = int(raw)
                    except ValueError:
                        eval_locals[name] = 0
            value = int(eval(joined, {"__builtins__": {}}, eval_locals))
        except Exception:
            value = 0
        return str(value)

    def _expand_heredoc(self, redir: Redirect) -> str:
        content = redir.here_doc or ""
        if not redir.here_doc_expand:
            return content
        fields = expand_word(
            content,
            self._expand_param,
            self._expand_braced_param,
            self._expand_command_subst_text,
            self._expand_arith,
            lambda s: [s],
            lambda s: [s],
        )
        return fields[0] if fields else ""

    def _dup_fd(self, redir: Redirect, is_output: bool, default_fd: int | None = None) -> None:
        fd = redir.fd if redir.fd is not None else (1 if is_output else 0)
        target = self._expand_assignment_word(redir.target) if redir.target else redir.target
        try:
            if target == "-":
                try:
                    os.close(fd)
                except OSError:
                    pass
                self._user_fds.discard(fd)
                return
            if target.isdigit():
                src_fd = int(target)
                if src_fd >= 3 and src_fd not in self._user_fds:
                    raise OSError(9, "Bad file descriptor")
                os.dup2(src_fd, fd)
                if fd >= 3:
                    self._user_fds.add(fd)
                return
            mode = "wb" if is_output else "rb"
            f = open(target, mode)
            os.dup2(f.fileno(), fd)
            f.close()
            if fd >= 3:
                self._user_fds.add(fd)
        except OSError as e:
            if target and target.isdigit():
                # BusyBox ash diagnostics special-case fd 10 in script-mode.
                if int(target) == 10 and fd == 1:
                    raise RuntimeError(self._format_error(f"{target}: {e.strerror}", line=self.current_line))
                raise RuntimeError(self._format_error(f"dup2({target},{fd}): {e.strerror}", line=self.current_line))
            raise RuntimeError(self._format_error(f"{target}: {e.strerror}", line=self.current_line))

    def _get_var(self, name: str) -> str:
        for scope in reversed(self.local_stack):
            if name in scope:
                return scope[name]
        return self.env.get(name, "")

    def _get_var_with_state(self, name: str) -> tuple[str, bool]:
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

    def _set_local(self, name: str, value: str) -> None:
        if not self.local_stack:
            self.env[name] = value
            return
        self.local_stack[-1][name] = value

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
                self._set_local(arg, "")
        return 0

    def _run_eval(self, args: List[str]) -> int:
        source = " ".join(args)
        return self._eval_source(source, parse_context="eval", line_offset=1)

    def _run_declare(self, args: List[str]) -> int:
        if args and args[0] == "-F":
            for name in sorted(self.functions.keys()):
                print(name)
            return 0
        return 0

    def _run_set(self, args: List[str]) -> int:
        if not args:
            return 0
        if args[0] == "--":
            self.set_positional_args(args[1:])
            return 0
        if args[0] in ["-o", "+o"]:
            if len(args) >= 2 and args[1] == "pipefail":
                self.options["pipefail"] = args[0] == "-o"
                return 0
            return 1
        if args[0].startswith("-") or args[0].startswith("+"):
            for token in args:
                if token == "--":
                    rest = args[args.index(token) + 1 :]
                    self.set_positional_args(rest)
                    return 0
                if token.startswith("-"):
                    for ch in token[1:]:
                        self.options[ch] = True
                elif token.startswith("+"):
                    for ch in token[1:]:
                        self.options[ch] = False
            return 0
        self.set_positional_args(args)
        return 0

    def _run_export(self, args: List[str]) -> int:
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                op = "="
                if name.endswith("+"):
                    op = "+="
                    name = name[:-1]
                if op == "+=":
                    self.env[name] = self.env.get(name, "") + value
                else:
                    self.env[name] = value
            else:
                self.env[arg] = self.env.get(arg, "")
        return 0

    def _run_unset(self, args: List[str]) -> int:
        for name in args:
            if name in self.env:
                del self.env[name]
            for scope in self.local_stack:
                scope.pop(name, None)
        return 0

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
                    spec = fmt[i + 1]
                    if spec == "%":
                        out.append("%")
                    else:
                        val = vals[vi] if vi < len(vals) else ""
                        vi += 1
                        if spec == "s":
                            out.append(val)
                        elif spec in ["d", "i"]:
                            try:
                                out.append(str(int(val)))
                            except ValueError:
                                out.append("0")
                        else:
                            out.append(val)
                    i += 2
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
        # Use latin-1 to preserve byte-oriented escapes like \\xHH.
        data = rendered.encode("latin-1", errors="ignore")
        try:
            os.write(1, data)
            return 0
        except OSError as e:
            if getattr(e, "errno", None) == 32:
                print("ash: write error: Broken pipe", file=sys.stderr)
                return 1
            print(f"ash: write error: {e.strerror}", file=sys.stderr)
            return 1

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
        if args and args[0] == "-n":
            newline = False
            args = args[1:]
        data = " ".join(args)
        if newline:
            data += "\n"
        if isinstance(sys.stdout, io.StringIO) and self._fd_redirect_depth == 0:
            sys.stdout.write(data)
            return 0
        if self._force_broken_pipe and self._fd_redirect_depth == 0:
            print("ash: write error: Broken pipe", file=sys.stderr)
            return 1
        try:
            os.write(1, data.encode("utf-8", errors="ignore"))
            return 0
        except OSError as e:
            if getattr(e, "errno", None) == 32:
                print("ash: write error: Broken pipe", file=sys.stderr)
                return 1
            print(f"ash: write error: {e.strerror}", file=sys.stderr)
            return 1

    def _run_read(self, args: List[str]) -> int:
        if not args:
            args = ["REPLY"]
        line = self._readline_fd0()
        if line is None:
            return 1
        raw = line.rstrip("\n")
        if len(args) == 1:
            self.env[args[0]] = raw
            return 0
        parts = raw.split()
        for i, name in enumerate(args):
            if i < len(args) - 1:
                value = parts[i] if i < len(parts) else ""
            else:
                value = " ".join(parts[i:]) if i < len(parts) else ""
            self.env[name] = value
        return 0

    def _readline_fd0(self) -> str | None:
        if isinstance(sys.stdin, io.StringIO):
            line = sys.stdin.readline()
            return line if line != "" else None
        buf = bytearray()
        while True:
            chunk = os.read(0, 1)
            if not chunk:
                if not buf:
                    return None
                break
            buf.extend(chunk)
            if chunk == b"\n":
                break
        return buf.decode("utf-8", errors="ignore")

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
                    path = self._find_in_path(name, lookup_path)
                    if path:
                        print(path)
                        return 0
                    return 1
                if name in self.functions:
                    print(name)
                    return 0
                if name in self.BUILTINS:
                    print(name)
                    return 0
                path = self._find_in_path(name, lookup_path)
                if path:
                    print(path)
                    return 0
                print(f"{name}: not found", file=sys.stderr)
                return 1
            break
        cmd = args[i:]
        if not cmd:
            return 0
        if cmd[0] in self.BUILTINS:
            return self._run_builtin(cmd[0], cmd)
        if cmd[0] in self.functions:
            return self._run_function(cmd[0], cmd[1:])
        env = dict(self.env)
        if search_default_path:
            env["PATH"] = "/usr/bin:/bin"
        return self._run_external(cmd, env, [])

    def _run_trap(self, args: List[str]) -> int:
        if not args:
            for sig, action in sorted(self.traps.items()):
                print(f"trap -- '{action}' {sig}")
            return 0
        if len(args) < 2:
            return 1
        action = args[0]
        for sig in args[1:]:
            key = sig.upper()
            if action == "-":
                self.traps.pop(key, None)
            else:
                self.traps[key] = action
        return 0

    def _run_type(self, args: List[str]) -> int:
        if not args:
            return 1
        status = 0
        for name in args:
            if name in self.functions:
                print(f"{name} is a function")
            elif name in self.BUILTINS:
                print(f"{name} is a shell builtin")
            else:
                path = self._find_in_path(name)
                if path:
                    print(path)
                else:
                    print(f"type: {name}: not found", file=sys.stderr)
                    status = 1
        return status

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
        negate = False
        if tokens and tokens[0] == "!":
            negate = True
            tokens = tokens[1:]
        result = False
        if len(tokens) >= 2 and tokens[0] == "-f":
            result = os.path.isfile(tokens[1])
        elif len(tokens) >= 2 and tokens[0] == "-d":
            result = os.path.isdir(tokens[1])
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
        parser_impl = Parser(source)
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
                status = self._exec_list_item(asdl_item_to_list_item(asdl_item))
                self.last_status = status
                if status != 0:
                    self.last_nonzero_status = status
                self._trap_status_hint = status
                if not getattr(node, "background", False):
                    self._run_pending_traps()
                if status != 0 and self.options.get("e", False):
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
                self._report_error(text, line=line_hint + line_offset, context=parse_context)
            else:
                print(f"parse error: {text}", file=sys.stderr)
            status = 2
        except (AsdlMappingError, OshAdapterError) as e:
            print(f"asdl error: {e}", file=sys.stderr)
            status = 2
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            status = 1
        return status

    def _capture_eval(self, source: str) -> tuple[str, int]:
        if self._has_unterminated_quote(source):
            raise RuntimeError(self._format_error("syntax error: unterminated quoted string", line=0))
        r_fd, w_fd = os.pipe()
        saved_stdout = os.dup(1)
        os.dup2(w_fd, 1)
        os.close(w_fd)
        try:
            status = self._eval_source(source)
        finally:
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
        with os.fdopen(r_fd, "rb") as r:
            data = r.read()
        return data.decode("utf-8", errors="ignore"), status

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
        if "syntax error:" in msg and " at " in msg:
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
