from __future__ import annotations

import argparse
import json
import os
import signal
import shlex
import sys
from typing import Dict, List, Tuple

from .parser import ParseError, Parser
from .asdl_map import AsdlMappingError, lst_list_item_to_asdl, lst_script_to_asdl
from .runtime import BreakLoop, ContinueLoop, Runtime, RuntimeError

VALID_STARTUP_OPTION_LETTERS = set("aCefnuvxIimqVEbpslr")
DEFAULT_BASH_COMPAT = "50"


def _set_proc_comm() -> None:
    name = os.environ.get("MCTASH_COMM_NAME", "ash")
    try:
        with open("/proc/self/comm", "w", encoding="utf-8") as f:
            f.write((name[:15] if name else "ash") + "\n")
    except OSError:
        pass


def _resolve_invocation_name(argv0: str) -> str:
    override = os.environ.get("MCTASH_ARG0", "")
    if override:
        return os.path.basename(override)
    return os.path.basename(argv0)


def _resolve_mode_from_name(name: str) -> str:
    low = (name or "").lower()
    if low in {"sh", "ash", "dash"}:
        return "posix"
    if low in {"mctash", "ptash", "bash"}:
        return "bash"
    return ""


def _resolve_invocation_mode(argv0: str, startup_changes: Dict[str, bool]) -> str:
    if "posix" in startup_changes:
        return "posix" if startup_changes["posix"] else "bash"
    name_mode = _resolve_mode_from_name(_resolve_invocation_name(argv0))
    if name_mode:
        return name_mode
    env_mode = os.environ.get("MCTASH_MODE", "").strip().lower()
    if env_mode in {"posix", "bash"}:
        return env_mode
    return "bash"


def _apply_invocation_mode(mode: str, startup_changes: Dict[str, bool]) -> None:
    # Keep active mode explicit for runtime diagnostics/policy routing.
    os.environ["MCTASH_MODE"] = mode
    if mode == "posix":
        startup_changes["posix"] = True
        return
    startup_changes["posix"] = False
    if not os.environ.get("BASH_COMPAT"):
        os.environ["BASH_COMPAT"] = DEFAULT_BASH_COMPAT


def main(argv: List[str] | None = None) -> int:
    _set_proc_comm()
    argv = list(argv) if argv is not None else sys.argv[1:]
    startup_changes, argv, startup_err = _parse_startup_options(argv)
    if startup_err is not None:
        print(f"mctash: {startup_err}", file=sys.stderr)
        return 2
    dump_mode = str(startup_changes.get("__dump_mode__", "strings"))
    if startup_changes.get("D", False):
        # bash: -D implies -n (parse/dump only, no execution).
        startup_changes["n"] = True
    mode = _resolve_invocation_mode(sys.argv[0], startup_changes)
    _apply_invocation_mode(mode, startup_changes)
    if argv and argv[0] == "-c":
        if len(argv) < 2:
            print("mctash: -c requires an argument", file=sys.stderr)
            return 2
        source = argv[1]
        if len(argv) > 2:
            script_name = argv[2]
        else:
            script_name = _resolve_invocation_name(sys.argv[0])
            if script_name in {"__main__.py", "python", "python3", "python3.10"}:
                script_name = "bash" if os.environ.get("BASH_COMPAT") else "mctash"
        script_args = argv[3:] if len(argv) > 3 else []
        rt = Runtime()
        _apply_startup_options(rt, startup_changes)
        rt.c_string_mode = True
        rt.set_script_name(script_name)
        rt.set_positional_args(script_args)
        login_shell = startup_changes.get("__login__", False) or os.path.basename(sys.argv[0]).startswith("-")
        interactive = bool(rt.options.get("i", False))
        rt.set_login_shell(login_shell)
        rt.set_interactive_session(interactive)
        _source_startup_files(rt, mode=mode, login_shell=login_shell, interactive=interactive)
        if startup_changes.get("D", False):
            # bash always labels `-c` input as "-c" in dump output, even when
            # argv[0] for the script body is provided separately.
            return _emit_dump_strings(source, "-c", dump_mode)
        try:
            parser_impl = Parser(source, aliases=rt.aliases)
            while True:
                item = parser_impl.parse_next()
                if item is None:
                    break
                rt.current_line = parser_impl.last_line
                src_item = parser_impl.last_source_text()
                if src_item is not None:
                    rt.add_history_entry(src_item.rstrip("\n"))
                    if rt.options.get("v", False):
                        line = src_item if src_item.endswith("\n") else src_item + "\n"
                        sys.stderr.write(line)
                if rt.options.get("n", False):
                    rt.last_status = 0
                    rt._trap_status_hint = 0
                    continue
                if parser_impl.last_lst_item is None:
                    raise ParseError("internal parse error: missing LST list item")
                asdl_item = lst_list_item_to_asdl(parser_impl.last_lst_item, strict=True)
                rt.last_status = rt._exec_asdl_list_item(asdl_item)
                errexit_item_exempt = rt._take_errexit_item_exempt()
                if rt.last_status != 0:
                    rt.last_nonzero_status = rt.last_status
                rt._trap_status_hint = rt.last_status
                if not getattr(item, "background", False):
                    rt._run_pending_traps()
                if rt.last_status != 0 and rt.options.get("e", False) and not errexit_item_exempt:
                    raise SystemExit(rt.last_status)
            return rt._run_exit_trap(rt.last_status)
        except ParseError as e:
            text, line = _normalize_parse_error(str(e))
            if line is not None:
                print(f"{script_name or 'mctash -c'}: line {line}: {text}", file=sys.stderr)
            else:
                print(f"parse error: {text}", file=sys.stderr)
            if "bad substitution" in text:
                return 127 if os.environ.get("MCTASH_DIAG_STYLE", "").strip().lower() == "bash" else 2
            return 2
        except RuntimeError as e:
            msg = str(e)
            print(msg, file=sys.stderr)
            return rt._runtime_error_status(msg)
        except (BreakLoop, ContinueLoop):
            return 1
        except SystemExit as e:
            code = int(e.code) if e.code is not None else 0
            return rt._run_exit_trap(code)
        except KeyboardInterrupt:
            return 130

    dump_lst = False
    if "--dump-lst" in argv:
        argv = [a for a in argv if a != "--dump-lst"]
        dump_lst = True

    # Re-parse startup options before script split to preserve `-s arg...` semantics.
    startup_changes2, argv2, startup_err2 = _parse_startup_options(argv)
    if startup_err2 is not None:
        print(f"mctash: {startup_err2}", file=sys.stderr)
        return 2
    startup_changes.update(startup_changes2)
    if startup_changes.get("D", False):
        startup_changes["n"] = True
    if "__dump_mode__" in startup_changes2:
        dump_mode = str(startup_changes2.get("__dump_mode__", dump_mode))
    mode = _resolve_invocation_mode(sys.argv[0], startup_changes)
    _apply_invocation_mode(mode, startup_changes)

    cli_opts, script, script_args = _split_cli_argv(argv2)
    shebang_args: List[str] = []

    if script:
        with open(script, "r", encoding="utf-8", errors="surrogateescape") as f:
            source = f.read()
        source, shebang_args = _strip_shebang_and_args(source)
    else:
        source = ""

    full_argv = cli_opts + shebang_args + ([script] if script else []) + script_args
    startup_changes3, full_argv, startup_err3 = _parse_startup_options(full_argv)
    if startup_err3 is not None:
        print(f"mctash: {startup_err3}", file=sys.stderr)
        return 2
    startup_changes.update(startup_changes3)
    if startup_changes.get("D", False):
        startup_changes["n"] = True
    if "__dump_mode__" in startup_changes3:
        dump_mode = str(startup_changes3.get("__dump_mode__", dump_mode))
    mode = _resolve_invocation_mode(sys.argv[0], startup_changes)
    _apply_invocation_mode(mode, startup_changes)
    _, full_script, full_script_args = _split_cli_argv(full_argv)
    args = argparse.Namespace(
        dump_lst=dump_lst,
        script=full_script,
        script_args=full_script_args,
    )

    if args.dump_lst:
        script = Parser(source).parse_script()
        payload = lst_script_to_asdl(script.lst, strict=True) if script.lst else {}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    rt = Runtime()
    _apply_startup_options(rt, startup_changes)
    rt.c_string_mode = False
    rt.set_script_name(args.script or "")
    rt.set_positional_args(args.script_args)
    login_shell = startup_changes.get("__login__", False) or os.path.basename(sys.argv[0]).startswith("-")
    interactive = bool(rt.options.get("i", False)) or (args.script is None and os.isatty(0))
    rt.set_login_shell(login_shell)
    rt.set_interactive_session(interactive)

    if interactive and args.script is None:
        if "m" not in startup_changes:
            rt.options["m"] = True
        _source_startup_files(rt, mode=mode, login_shell=login_shell, interactive=True)
        return _run_interactive(rt)

    _source_startup_files(rt, mode=mode, login_shell=login_shell, interactive=False)

    if args.script is None:
        source = sys.stdin.read()
    if startup_changes.get("D", False):
        return _emit_dump_strings(source, args.script or "-", dump_mode)

    try:
        parser_impl = Parser(source, aliases=rt.aliases)
        while True:
            item = parser_impl.parse_next()
            if item is None:
                break
            rt.current_line = parser_impl.last_line
            src_item = parser_impl.last_source_text()
            if src_item is not None:
                rt.add_history_entry(src_item.rstrip("\n"))
                if rt.options.get("v", False):
                    line = src_item if src_item.endswith("\n") else src_item + "\n"
                    sys.stderr.write(line)
            if rt.options.get("n", False):
                rt.last_status = 0
                rt._trap_status_hint = 0
                continue
            if parser_impl.last_lst_item is None:
                raise ParseError("internal parse error: missing LST list item")
            asdl_item = lst_list_item_to_asdl(parser_impl.last_lst_item, strict=True)
            rt.last_status = rt._exec_asdl_list_item(asdl_item)
            errexit_item_exempt = rt._take_errexit_item_exempt()
            if rt.last_status != 0:
                rt.last_nonzero_status = rt.last_status
            rt._trap_status_hint = rt.last_status
            if not getattr(item, "background", False):
                rt._run_pending_traps()
            if rt.last_status != 0 and rt.options.get("e", False) and not errexit_item_exempt:
                raise SystemExit(rt.last_status)
        return rt._run_exit_trap(rt.last_status)
    except ParseError as e:
        msg = str(e)
        text, line_hint = _normalize_parse_error(msg)
        if args.script:
            if line_hint is not None:
                print(f"{args.script}: line {line_hint}: {text}", file=sys.stderr)
            else:
                print(f"{args.script}: {text}", file=sys.stderr)
        else:
            print(f"parse error: {text}", file=sys.stderr)
        if "bad substitution" in text:
            return 127 if os.environ.get("MCTASH_DIAG_STYLE", "").strip().lower() == "bash" else 2
        return 2
    except AsdlMappingError as e:
        print(f"asdl error: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        msg = str(e)
        print(msg, file=sys.stderr)
        return rt._runtime_error_status(msg)
    except (BreakLoop, ContinueLoop):
        return 1
    except SystemExit as e:
        code = int(e.code) if e.code is not None else 0
        return rt._run_exit_trap(code)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())


def _split_cli_argv(argv: List[str]) -> Tuple[List[str], str | None, List[str]]:
    if not argv:
        return [], None, []
    opts: List[str] = []
    script: str | None = None
    script_args: List[str] = []
    it = iter(argv)
    for arg in it:
        if arg == "-s":
            opts.append(arg)
            script = None
            script_args = list(it)
            break
        if script is None and not arg.startswith("-"):
            script = arg
            script_args = list(it)
            break
        opts.append(arg)
    return opts, script, script_args


def _option_name_to_letter(name: str) -> str | None:
    mapping = {
        "allexport": "a",
        "noclobber": "C",
        "errexit": "e",
        "noglob": "f",
        "noexec": "n",
        "nounset": "u",
        "verbose": "v",
        "xtrace": "x",
        "ignoreeof": "I",
        "interactive": "i",
        "monitor": "m",
        "vi": "V",
        "emacs": "E",
        "notify": "b",
        "nolog": "q",
        "debug": "debug",
        "quiet": "q",
        "stdin": "s",
        "privileged": "p",
        "restricted": "r",
        "posix": "posix",
    }
    return mapping.get(name.lower())


def _parse_startup_options(argv: List[str]) -> Tuple[Dict[str, bool], List[str], str | None]:
    changes: Dict[str, bool] = {}
    out: List[str] = []
    passthrough_long = {"--dump-lst"}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ["-c", "-s", "--"]:
            out.extend(argv[i:])
            break
        if arg in passthrough_long:
            out.append(arg)
            i += 1
            continue
        if arg == "--posix":
            changes["posix"] = True
            i += 1
            continue
        if arg == "--verbose":
            changes["v"] = True
            i += 1
            continue
        if arg == "--dump-strings":
            changes["D"] = True
            changes["__dump_mode__"] = "strings"
            i += 1
            continue
        if arg == "--dump-po-strings":
            changes["D"] = True
            changes["__dump_mode__"] = "po"
            i += 1
            continue
        if arg == "--bash":
            changes["posix"] = False
            i += 1
            continue
        if arg.startswith("--"):
            return changes, out, f"illegal option name: {arg[2:]}"
        if arg in ["-o", "+o"]:
            if i + 1 >= len(argv):
                return changes, out, f"{arg} requires an argument"
            name = argv[i + 1]
            if name == "pipefail":
                changes["pipefail"] = arg == "-o"
            else:
                letter = _option_name_to_letter(name)
                if letter is not None:
                    changes[letter] = arg == "-o"
                else:
                    return changes, out, f"illegal option name: {name}"
            i += 2
            continue
        if (arg.startswith("-") or arg.startswith("+")) and len(arg) > 1 and not arg.startswith("--"):
            on = arg[0] == "-"
            chars = arg[1:]
            if "o" in chars:
                # Keep `-o/+o name` handling simple and explicit.
                if len(chars) != 1:
                    return changes, out, "illegal option grouping with -o/+o"
                out.append(arg)
                out.extend(argv[i + 1 :])
                break
            special = [ch for ch in chars if ch in {"c", "s"}]
            if len(special) > 1:
                return changes, out, "illegal option grouping with -c/-s"
            for ch in chars:
                if ch in {"c", "s"}:
                    continue
                if ch == "D":
                    changes["D"] = on
                    if on:
                        changes["__dump_mode__"] = "strings"
                    continue
                if ch not in VALID_STARTUP_OPTION_LETTERS:
                    return changes, out, f"illegal option -- {ch}"
                if ch == "l":
                    changes["__login__"] = on
                    continue
                changes[ch] = on
            if special:
                if not on:
                    return changes, out, f"illegal option -- {special[0]}"
                out.append(f"-{special[0]}")
                out.extend(argv[i + 1 :])
                break
            i += 1
            continue
        out.append(arg)
        out.extend(argv[i + 1 :])
        break
    if i >= len(argv):
        return changes, [], None
    return changes, out, None


def _apply_startup_options(rt: Runtime, changes: Dict[str, bool]) -> None:
    for k, v in changes.items():
        if k.startswith("__"):
            continue
        rt.options[k] = v
    if rt.options.get("r", False):
        rt._activate_restricted_mode()
    # ash behavior: vi/emacs modes are mutually exclusive.
    if rt.options.get("V", False):
        rt.options["E"] = False
    if rt.options.get("E", False):
        rt.options["V"] = False


def _extract_dollar_quoted_strings(source: str) -> List[Tuple[int, str]]:
    """Return (line, raw_text) for every $"..." occurrence in shell source."""
    out: List[Tuple[int, str]] = []
    i = 0
    line = 1
    mode = "plain"
    while i < len(source):
        ch = source[i]
        if ch == "\n":
            line += 1
        if mode == "plain":
            if ch == "\\":
                i += 2
                continue
            if ch == "#":
                # Shell comments begin in plain mode and run to end-of-line.
                i += 1
                while i < len(source) and source[i] != "\n":
                    i += 1
                continue
            if ch == "'":
                mode = "single"
                i += 1
                continue
            if ch == '"':
                mode = "double"
                i += 1
                continue
            if ch == "$" and i + 1 < len(source) and source[i + 1] == '"':
                j = i + 2
                text: List[str] = []
                start_line = line
                while j < len(source):
                    c = source[j]
                    if c == "\n":
                        line += 1
                    if c == "\\" and j + 1 < len(source):
                        text.append(c)
                        text.append(source[j + 1])
                        j += 2
                        continue
                    if c == '"':
                        out.append((start_line, "".join(text)))
                        i = j + 1
                        break
                    text.append(c)
                    j += 1
                else:
                    # Unterminated quote: stop scanning at EOF.
                    i = len(source)
                continue
            i += 1
            continue
        if mode == "single":
            if ch == "'":
                mode = "plain"
            i += 1
            continue
        if mode == "double":
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                mode = "plain"
            i += 1
            continue
    return out


def _escape_po_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _emit_dump_strings(source: str, source_name: str, mode: str) -> int:
    entries = _extract_dollar_quoted_strings(source)
    if mode == "po":
        for line, text in entries:
            esc = _escape_po_text(text)
            print(f"#: {source_name}:{line}")
            print(f'msgid "{esc}"')
            print('msgstr ""')
        return 0
    for _, text in entries:
        esc = _escape_po_text(text)
        print(f'"{esc}"')
    return 0


def _source_startup_files(rt: Runtime, *, mode: str, login_shell: bool, interactive: bool) -> None:
    if login_shell:
        login_files: list[str]
        if mode == "bash":
            login_files = [
                "/etc/profile",
                os.path.expanduser("~/.bash_profile"),
                os.path.expanduser("~/.bash_login"),
                os.path.expanduser("~/.profile"),
            ]
        else:
            login_files = ["/etc/profile", os.path.expanduser("~/.profile")]
        loaded_user = False
        for path in login_files:
            if loaded_user and path.startswith(os.path.expanduser("~/")):
                continue
            if os.path.exists(path):
                rt._run_source(path, [])
                if path.startswith(os.path.expanduser("~/")):
                    loaded_user = True
    if interactive:
        if mode == "bash":
            bashrc = os.path.expanduser("~/.bashrc")
            if os.path.exists(bashrc):
                rt._run_source(bashrc, [])
        else:
            env_path = rt._get_var("ENV")
            if env_path:
                p = os.path.expanduser(env_path)
                if os.path.exists(p):
                    rt._run_source(p, [])
        return
    # Non-interactive startup files.
    if mode == "bash":
        env_path = rt._get_var("BASH_ENV")
        if env_path:
            p = os.path.expanduser(env_path)
            if os.path.exists(p):
                rt._run_source(p, [])


def _try_parse_complete(source: str, aliases: Dict[str, str]) -> tuple[bool, str | None]:
    try:
        p = Parser(source, aliases=aliases)
        while True:
            item = p.parse_next()
            if item is None:
                break
        return True, None
    except ParseError as e:
        msg = str(e)
        lower = msg.lower()
        if "end of file" in lower or "unterminated" in lower or "missing end_python" in lower:
            return False, None
        if msg.startswith("expected "):
            return False, None
        return True, msg


def _configure_line_editor(rt: Runtime) -> None:
    try:
        import readline  # noqa: F401
    except Exception:
        return
    try:
        if rt.options.get("V", False):
            readline.parse_and_bind("set editing-mode vi")
        else:
            readline.parse_and_bind("set editing-mode emacs")
    except Exception:
        pass


def _expand_prompt(rt: Runtime, prompt: str) -> str:
    return rt._expand_prompt_string(prompt)


def _expand_history_bang(rt: Runtime, line: str) -> tuple[str | None, str | None]:
    txt = line.rstrip("\n")
    if not txt.startswith("!"):
        return txt, None
    if txt == "!!":
        idx = rt._history_resolve("-1")
    elif txt.startswith("!-") and txt[2:].isdigit():
        idx = rt._history_resolve("-" + txt[2:])
    elif txt[1:].isdigit():
        idx = rt._history_resolve(txt[1:])
    else:
        return txt, None
    if idx is None or idx < 0 or idx >= len(rt._history):
        return None, "event not found"
    return rt._history[idx], None


def _run_interactive(rt: Runtime) -> int:
    _configure_line_editor(rt)
    buffer: List[str] = []
    status = 0
    eof_count = 0
    while True:
        try:
            if not buffer:
                pcmd = rt.env.get("PROMPT_COMMAND", "")
                if pcmd:
                    try:
                        rt._eval_source(pcmd, propagate_exit=False, propagate_return=False, parse_context="prompt")
                    except Exception:
                        pass
            prompt_raw = rt.env.get("PS2", "> ") if buffer else rt.env.get("PS1", "$ ")
            timeout_secs: int | None = None
            tmout_raw = rt._get_var("TMOUT")
            if tmout_raw.isdigit():
                t = int(tmout_raw, 10)
                if t > 0:
                    timeout_secs = t
            old_handler = None
            armed = False
            if timeout_secs is not None and hasattr(signal, "SIGALRM"):
                old_handler = signal.getsignal(signal.SIGALRM)

                def _tmout_handler(_signum, _frame):
                    raise TimeoutError()

                signal.signal(signal.SIGALRM, _tmout_handler)
                signal.alarm(timeout_secs)
                armed = True
            try:
                line = input(_expand_prompt(rt, prompt_raw))
            finally:
                if armed and hasattr(signal, "SIGALRM"):
                    signal.alarm(0)
                    if old_handler is not None:
                        signal.signal(signal.SIGALRM, old_handler)
            eof_count = 0
        except EOFError:
            if rt.options.get("I", False) and os.isatty(0):
                eof_count += 1
                print()
                if eof_count >= 50:
                    break
                continue
            print()
            break
        except KeyboardInterrupt:
            print()
            status = 130
            rt.last_status = status
            buffer.clear()
            continue
        except TimeoutError:
            print("timed out waiting for input: auto-logout")
            status = 0
            rt.last_status = status
            rt._trap_status_hint = status
            break
        if not buffer:
            expanded, err = _expand_history_bang(rt, line + "\n")
            if err is not None:
                print(err, file=sys.stderr)
                status = 1
                rt.last_status = status
                rt.last_nonzero_status = status
                rt._trap_status_hint = status
                continue
            if expanded is not None and expanded != line:
                print(expanded)
                line = expanded
        buffer.append(line + "\n")
        src = "".join(buffer)
        complete, hard_err = _try_parse_complete(src, rt.aliases)
        if not complete:
            continue
        if hard_err is not None:
            text, line_hint = _normalize_parse_error(hard_err)
            if line_hint is not None:
                print(f"mctash: line {line_hint}: {text}", file=sys.stderr)
            else:
                print(f"mctash: {text}", file=sys.stderr)
            status = 2
            rt.last_status = status
            if status != 0:
                rt.last_nonzero_status = status
            rt._trap_status_hint = status
            buffer.clear()
            continue
        rt.add_history_entry(src.rstrip("\n"))
        try:
            status = rt._eval_source(src, propagate_exit=True)
        except SystemExit as e:
            code = int(e.code) if e.code is not None else 0
            rt.last_status = code
            return rt._run_exit_trap(code)
        except KeyboardInterrupt:
            print()
            status = 130
            rt.last_status = status
            rt.last_nonzero_status = status
            rt._trap_status_hint = status
            buffer.clear()
            continue
        rt.last_status = status
        if status != 0:
            rt.last_nonzero_status = status
        rt._trap_status_hint = status
        buffer.clear()
    return rt._run_exit_trap(rt.last_status)


def _strip_shebang_and_args(source: str) -> Tuple[str, List[str]]:
    if not source.startswith("#!"):
        return source, []
    first_line, rest = source.split("\n", 1) if "\n" in source else (source, "")
    shebang = first_line[2:].strip()
    if not shebang:
        return rest, []
    tokens = shlex.split(shebang)
    args: List[str] = []
    mctash_idx = _find_mctash_index(tokens)
    if mctash_idx is not None:
        args = tokens[mctash_idx + 1 :]
    return rest, args


def _find_mctash_index(tokens: List[str]) -> int | None:
    for i, tok in enumerate(tokens):
        base = os.path.basename(tok)
        if base in ["mctash", "mctash.py", "mctash.exe"]:
            return i
    return None


def _normalize_parse_error(msg: str) -> tuple[str, int | None]:
    if msg.startswith("expected function name at "):
        where = msg[len("expected function name at ") :]
        line_s = where.split(":", 1)[0]
        line = int(line_s) if line_s.isdigit() else None
        return "syntax error: invalid function name", line
    if msg.startswith("expected do at "):
        where = msg[len("expected do at ") :]
        line_s = where.split(":", 1)[0]
        line = int(line_s) if line_s.isdigit() else None
        return 'syntax error: unexpected token (expecting "do")', line
    if msg.startswith("expected then at "):
        where = msg[len("expected then at ") :]
        line_s = where.split(":", 1)[0]
        return 'syntax error: unexpected ")"', int(line_s) if line_s.isdigit() else None
    if msg.startswith("expected done at "):
        where = msg[len("expected done at ") :]
        line_s = where.split(":", 1)[0]
        return 'syntax error: unexpected end of file (expecting "done")', int(line_s) if line_s.isdigit() else None
    if "syntax error:" in msg and " at " in msg:
        text, where = msg.rsplit(" at ", 1)
        line_s = where.split(":", 1)[0]
        return text, int(line_s) if line_s.isdigit() else None
    return msg, None
