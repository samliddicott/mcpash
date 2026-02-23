from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from typing import List, Tuple

from .parser import ParseError, Parser
from .asdl_map import AsdlMappingError, lst_list_item_to_asdl, lst_script_to_asdl
from .osh_adapter import OshAdapterError, asdl_item_to_list_item
from .runtime import BreakLoop, ContinueLoop, Runtime, RuntimeError


def main(argv: List[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    cli_opts, script, script_args = _split_cli_argv(argv)
    shebang_args: List[str] = []

    if script:
        with open(script, "r", encoding="utf-8") as f:
            source = f.read()
        source, shebang_args = _strip_shebang_and_args(source)
    else:
        source = sys.stdin.read()

    full_argv = cli_opts + shebang_args + ([script] if script else []) + script_args

    parser = argparse.ArgumentParser(prog="mctash")
    parser.add_argument("--dump-lst", action="store_true", help="print LST as ASDL-like JSON and exit")
    parser.add_argument("script", nargs="?", help="script file to run")
    parser.add_argument("script_args", nargs=argparse.REMAINDER, help="args passed to the script")
    args = parser.parse_args(full_argv)

    if args.dump_lst:
        script = Parser(source).parse_script()
        payload = lst_script_to_asdl(script.lst, strict=True) if script.lst else {}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    rt = Runtime()
    rt.set_script_name(args.script or "")
    rt.set_positional_args(args.script_args)
    try:
        parser_impl = Parser(source)
        while True:
            item = parser_impl.parse_next()
            if item is None:
                break
            if parser_impl.last_lst_item is None:
                raise ParseError("internal parse error: missing LST list item")
            asdl_item = lst_list_item_to_asdl(parser_impl.last_lst_item, strict=True)
            rt.last_status = rt._exec_list_item(asdl_item_to_list_item(asdl_item))
        return rt.last_status
    except ParseError as e:
        print(f"parse error: {e}", file=sys.stderr)
        return 2
    except (AsdlMappingError, OshAdapterError) as e:
        print(f"asdl error: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"runtime error: {e}", file=sys.stderr)
        return 1
    except (BreakLoop, ContinueLoop):
        return 1
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0


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
        if script is None and not arg.startswith("-"):
            script = arg
            script_args = list(it)
            break
        opts.append(arg)
    return opts, script, script_args


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
