from __future__ import annotations

import glob
import io
import os
import subprocess
import sys
import tempfile
import threading
import fnmatch
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
from .parser import Parser


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
    def __init__(self) -> None:
        self.last_status = 0
        self.env: Dict[str, str] = dict(os.environ)
        self.positional: List[str] = []
        self.functions: Dict[str, ListNode] = {}
        self.local_stack: List[Dict[str, str]] = []
        self.script_name: str = ""
        self.options: Dict[str, bool] = {}

    def set_positional_args(self, args: List[str]) -> None:
        self.positional = list(args)

    def set_script_name(self, name: str) -> None:
        self.script_name = name

    def run(self, script: Script) -> int:
        return self._exec_list(script.body)

    def _exec_list(self, node: ListNode) -> int:
        status = 0
        for item in node.items:
            status = self._exec_list_item(item)
            if status != 0 and self.options.get("e", False):
                raise SystemExit(status)
        return status

    def _exec_list_item(self, item) -> int:
        if getattr(item, "background", False):
            thread = threading.Thread(target=self._exec_and_or, args=(item.node,))
            thread.daemon = True
            thread.start()
            return 0
        return self._exec_and_or(item.node)

    def _exec_and_or(self, node: AndOr) -> int:
        status = self._exec_pipeline(node.pipelines[0])
        for op, pipeline in zip(node.operators, node.pipelines[1:]):
            if op == "&&":
                if status == 0:
                    status = self._exec_pipeline(pipeline)
            elif op == "||":
                if status != 0:
                    status = self._exec_pipeline(pipeline)
        return status

    def _exec_pipeline(self, node: Pipeline) -> int:
        if len(node.commands) == 1:
            status = self._exec_command(node.commands[0])
            return 0 if (node.negate and status != 0) else (1 if node.negate and status == 0 else status)
        procs: List[subprocess.Popen] = []
        prev = None
        for i, cmd in enumerate(node.commands):
            if not isinstance(cmd, SimpleCommand):
                return self._exec_command(cmd)
            argv = self._expand_argv(cmd.argv)
            if not argv:
                return 2
            stdin = prev.stdout if prev is not None else None
            stdout = subprocess.PIPE if i < len(node.commands) - 1 else None
            stdin, stdout = self._apply_redirects(cmd.redirects, stdin, stdout)
            proc = subprocess.Popen(argv, stdin=stdin, stdout=stdout, env=self.env)
            procs.append(proc)
            if prev is not None:
                prev.stdout.close()
            prev = proc
        status = procs[-1].wait()
        for p in procs[:-1]:
            p.wait()
        if node.negate:
            return 0 if status != 0 else 1
        return status

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
            return status
        if isinstance(node, WhileCommand):
            last = 0
            while True:
                cond_status = self._exec_list(node.cond)
                should_run = cond_status != 0 if node.until else cond_status == 0
                if not should_run:
                    break
                try:
                    last = self._exec_list(node.body)
                except ContinueLoop:
                    continue
                except BreakLoop as e:
                    if e.count > 1:
                        raise BreakLoop(e.count - 1)
                    break
            return last
        if isinstance(node, SimpleCommand):
            local_env = dict(self.env)
            for assign in node.assignments:
                value = self._expand_word(assign.value)
                if assign.op == "+=":
                    local_env[assign.name] = local_env.get(assign.name, "") + value
                else:
                    local_env[assign.name] = value

            argv = self._expand_argv(node.argv)
            if not argv:
                if node.redirects:
                    with self._redirected_fds(node.redirects):
                        pass
                self.env.update(local_env)
                return 0
            name = argv[0]
            if name in ["cd", "exit", ":", "return", ".", "source", "local", "eval", "declare", "[", "[[", "test", "set", "export", "unset", "shift", "printf", "read", "true", "false", "command", "break", "continue", "trap"]:
                try:
                    with self._redirected_fds(node.redirects):
                        status = self._run_builtin(name, argv)
                finally:
                    self.env.update(local_env)
                return status
            if name in self.functions:
                try:
                    with self._redirected_fds(node.redirects):
                        status = self._run_function(name, argv[1:])
                finally:
                    self.env.update(local_env)
                return status
            status = self._run_external(argv, local_env, node.redirects)
            self.env.update(local_env)
            return status
        if isinstance(node, RedirectCommand):
            with self._redirected_fds(node.redirects):
                return self._exec_command(node.child)
        return 2

    def _run_subshell(self, body: ListNode) -> int:
        saved_env = dict(self.env)
        saved_local = [dict(s) for s in self.local_stack]
        saved_positional = list(self.positional)
        saved_cwd = os.getcwd()
        try:
            return self._exec_list(body)
        finally:
            self.env = saved_env
            self.local_stack = saved_local
            self.positional = saved_positional
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
        for item in items:
            self.env[node.name] = item
            try:
                status = self._exec_list(node.body)
            except ContinueLoop:
                continue
            except BreakLoop as e:
                if e.count > 1:
                    raise BreakLoop(e.count - 1)
                break
        return status

    def _run_case(self, node: CaseCommand) -> int:
        value_parts = self._expand_argv([node.value])
        value = value_parts[0] if value_parts else ""
        for item in node.items:
            for pat in item.patterns:
                if fnmatch.fnmatch(value, pat):
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
        if name == "read":
            return self._run_read(argv[1:])
        if name == "true":
            return 0
        if name == "false":
            return 1
        if name == "command":
            return self._run_command_builtin(argv[1:])
        if name == "trap":
            return self._run_trap(argv[1:])
        if name in ["[", "[[", "test"]:
            return self._run_test(name, argv[1:])
        if name == "exit":
            code = int(argv[1]) if len(argv) > 1 else self.last_status
            raise SystemExit(code)
        if name == "return":
            code = int(argv[1]) if len(argv) > 1 else self.last_status
            raise ReturnFromFunction(code)
        if name == ":":
            return 0
        if name == "break":
            count = int(argv[1]) if len(argv) > 1 else 1
            raise BreakLoop(count)
        if name == "continue":
            count = int(argv[1]) if len(argv) > 1 else 1
            raise ContinueLoop(count)
        return 2

    def _run_source(self, path: str, args: List[str]) -> int:
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except OSError:
            return 1
        parser_impl = Parser(source)
        saved_positional = list(self.positional)
        self.set_positional_args(args)
        status = 0
        try:
            while True:
                node = parser_impl.parse_next()
                if node is None:
                    break
                status = self._exec_list_item(node)
        except ReturnFromFunction as e:
            status = e.code
        finally:
            self.set_positional_args(saved_positional)
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

    def _run_external(self, argv: List[str], env: Dict[str, str], redirects: List[Redirect]) -> int:
        stdin, stdout = self._apply_redirects(redirects, None, None)
        try:
            proc = subprocess.run(argv, env=env, stdin=stdin, stdout=stdout)
            return proc.returncode
        finally:
            if stdin not in (None, sys.stdin):
                stdin.close()
            if stdout not in (None, sys.stdout):
                stdout.close()

    def _apply_redirects(
        self,
        redirects: List[Redirect],
        stdin: Optional[object],
        stdout: Optional[object],
    ) -> Tuple[Optional[object], Optional[object]]:
        for redir in redirects:
            target_fd = redir.fd
            if redir.op == "<":
                f = open(redir.target, "rb")
                if target_fd in (None, 0):
                    stdin = f
                else:
                    os.dup2(f.fileno(), target_fd)
            elif redir.op == ">":
                f = open(redir.target, "wb")
                if target_fd in (None, 1):
                    stdout = f
                else:
                    os.dup2(f.fileno(), target_fd)
            elif redir.op == ">>":
                f = open(redir.target, "ab")
                if target_fd in (None, 1):
                    stdout = f
                else:
                    os.dup2(f.fileno(), target_fd)
            elif redir.op == "<<":
                content = self._expand_heredoc(redir)
                f = tempfile.TemporaryFile()
                f.write(content.encode("utf-8"))
                f.seek(0)
                if target_fd in (None, 0):
                    stdin = f
                else:
                    os.dup2(f.fileno(), target_fd)
            elif redir.op == ">&":
                self._dup_fd(redir, is_output=True)
            elif redir.op == "<&":
                self._dup_fd(redir, is_output=False)
        return stdin, stdout

    @contextmanager
    def _redirected_fds(self, redirects: List[Redirect]):
        saved: List[Tuple[int, int]] = []
        try:
            for redir in redirects:
                fd = redir.fd if redir.fd is not None else (0 if redir.op in ["<", "<<"] else 1)
                saved_fd = os.dup(fd)
                saved.append((fd, saved_fd))
                if redir.op == "<":
                    f = open(redir.target, "rb")
                    os.dup2(f.fileno(), fd)
                    f.close()
                elif redir.op == ">":
                    f = open(redir.target, "wb")
                    os.dup2(f.fileno(), fd)
                    f.close()
                elif redir.op == ">>":
                    f = open(redir.target, "ab")
                    os.dup2(f.fileno(), fd)
                    f.close()
                elif redir.op == "<<":
                    content = self._expand_heredoc(redir)
                    f = tempfile.TemporaryFile()
                    f.write(content.encode("utf-8"))
                    f.seek(0)
                    os.dup2(f.fileno(), fd)
                    f.close()
                elif redir.op == ">&":
                    self._dup_fd(redir, is_output=True, default_fd=fd)
                elif redir.op == "<&":
                    self._dup_fd(redir, is_output=False, default_fd=fd)
            yield
        finally:
            for fd, saved_fd in saved:
                os.dup2(saved_fd, fd)
                os.close(saved_fd)

    def _expand_argv(self, words: List[Word]) -> List[str]:
        argv: List[str] = []
        for w in words:
            argv.extend(
                expand_word(
                    w.text,
                    self._expand_param,
                    self._expand_braced_param,
                    self._expand_command_subst_text,
                    self._expand_arith,
                    self._split_ifs,
                    self._glob_field,
                )
            )
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
        value, is_set = self._get_param_state(name)
        if (not is_set or value == "") and self.options.get("u", False) and name not in ["@", "*", "#"]:
            raise RuntimeError(f"unbound variable: {name}")
        return value

    def _expand_braced_param(
        self, name: str, op: str | None, arg: str | None, quoted: bool
    ) -> str | List[str]:
        if name == "@" and op is None:
            return list(self.positional)
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
        return self._capture_eval(cmd).rstrip("\n")

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
        try:
            value = int(eval(joined, {"__builtins__": {}}, {}))
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
            self._split_ifs,
            self._glob_field,
        )
        return fields[0] if fields else ""

    def _dup_fd(self, redir: Redirect, is_output: bool, default_fd: int | None = None) -> None:
        fd = redir.fd if redir.fd is not None else (1 if is_output else 0)
        target = redir.target
        if target == "-":
            os.close(fd)
            return
        if target.isdigit():
            os.dup2(int(target), fd)
            return
        mode = "wb" if is_output else "rb"
        f = open(target, mode)
        os.dup2(f.fileno(), fd)
        f.close()

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
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                op = "="
                if name.endswith("+"):
                    op = "+="
                    name = name[:-1]
                expanded = self._expand_word(value)
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
        return self._eval_source(source)

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
                expanded = self._expand_word(value)
                if op == "+=":
                    self.env[name] = self.env.get(name, "") + expanded
                else:
                    self.env[name] = expanded
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
                return 1
        if n < 0 or n > len(self.positional):
            return 1
        self.positional = self.positional[n:]
        return 0

    def _run_printf(self, args: List[str]) -> int:
        if not args:
            return 0
        fmt = args[0]
        vals = args[1:]
        out = []
        i = 0
        vi = 0
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
        sys.stdout.write("".join(out))
        return 0

    def _run_read(self, args: List[str]) -> int:
        if not args:
            return 1
        line = sys.stdin.readline()
        if line == "":
            return 1
        parts = line.rstrip("\n").split()
        for i, name in enumerate(args):
            value = parts[i] if i < len(parts) else ""
            self.env[name] = value
        return 0

    def _run_command_builtin(self, args: List[str]) -> int:
        if not args:
            return 0
        return self._run_external(args, dict(self.env), [])

    def _run_trap(self, args: List[str]) -> int:
        # Minimal stub: accept and ignore for now.
        return 0

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
        elif len(tokens) == 1:
            result = tokens[0] != ""
        return 0 if (result ^ negate) else 1

    def _eval_source(self, source: str) -> int:
        parser_impl = Parser(source)
        status = 0
        try:
            while True:
                node = parser_impl.parse_next()
                if node is None:
                    break
                status = self._exec_list_item(node)
        except ReturnFromFunction as e:
            status = e.code
        return status

    def _capture_eval(self, source: str) -> str:
        r_fd, w_fd = os.pipe()
        saved_stdout = os.dup(1)
        os.dup2(w_fd, 1)
        os.close(w_fd)
        try:
            self._eval_source(source)
        finally:
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)
        with os.fdopen(r_fd, "rb") as r:
            data = r.read()
        return data.decode("utf-8", errors="ignore")

    def _expand_command_subst(self, text: str) -> str:
        return self._expand_command_subst_text(text)
