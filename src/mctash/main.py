from __future__ import annotations

import argparse
import sys
from typing import List

from .lexer import tokenize
from .parser import ParseError, parse
from .runtime import Runtime


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mctash")
    parser.add_argument("script", nargs="?", help="script file to run")
    args = parser.parse_args(argv)

    if args.script:
        with open(args.script, "r", encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.read()

    tokens = list(tokenize(source))
    rt = Runtime()
    try:
        from .parser import Parser
        parser_impl = Parser(tokens)
        while True:
            node = parser_impl.parse_next()
            if node is None:
                break
            rt.last_status = rt._exec_and_or(node)
        return rt.last_status
    except ParseError as e:
        print(f"parse error: {e}", file=sys.stderr)
        return 2
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
