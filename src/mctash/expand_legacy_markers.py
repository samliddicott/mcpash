from __future__ import annotations

from typing import List

GLOB_PROTECT = {
    "*": "\ue001",
    "?": "\ue002",
    "[": "\ue003",
    "]": "\ue004",
    "\\": "\ue005",
    "-": "\ue007",
    "!": "\ue008",
}
GLOB_UNPROTECT = {v: k for k, v in GLOB_PROTECT.items()}
ESCAPED_SLASH_MARK = "\ue006"
QUOTED_EMPTY_MARK = "\ue00c"
MARKER_ESCAPE = "\ue00f"

_ESCAPE_TOKENS = {
    MARKER_ESCAPE: "0",
    GLOB_PROTECT["*"]: "1",
    GLOB_PROTECT["?"]: "2",
    GLOB_PROTECT["["]: "3",
    GLOB_PROTECT["]"]: "4",
    GLOB_PROTECT["\\"]: "5",
    ESCAPED_SLASH_MARK: "6",
    GLOB_PROTECT["-"]: "7",
    GLOB_PROTECT["!"]: "8",
    QUOTED_EMPTY_MARK: "9",
}
_UNESCAPE_TOKENS = {v: k for k, v in _ESCAPE_TOKENS.items()}


def escape_marker_literals(text: str) -> str:
    out: list[str] = []
    for ch in text:
        token = _ESCAPE_TOKENS.get(ch)
        if token is None:
            out.append(ch)
            continue
        out.append(MARKER_ESCAPE)
        out.append(token)
    return "".join(out)


def protect_glob_meta(s: str) -> str:
    return "".join(GLOB_PROTECT.get(ch, ch) for ch in s)


def unprotect_glob_meta(s: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == MARKER_ESCAPE and i + 1 < len(s):
            tok = s[i + 1]
            orig = _UNESCAPE_TOKENS.get(tok)
            if orig is not None:
                out.append(orig)
                i += 2
                continue
        out.append(GLOB_UNPROTECT.get(ch, "/" if ch == ESCAPED_SLASH_MARK else ch))
        i += 1
    return "".join(out)


def contains_glob_meta(text: str) -> bool:
    return any(c in text for c in ["*", "?", "[", GLOB_PROTECT["*"], GLOB_PROTECT["?"], GLOB_PROTECT["["], GLOB_PROTECT["]"], GLOB_PROTECT["\\"], GLOB_PROTECT["-"]])


def glob_pattern_for_match(text: str) -> str:
    protected = (
        text.replace(GLOB_PROTECT["*"], "[*]")
        .replace(GLOB_PROTECT["?"], "[?]")
        .replace(GLOB_PROTECT["["], "[[]")
        .replace(GLOB_PROTECT["]"], "[]]")
        .replace(GLOB_PROTECT["\\"], "[\\\\]")
        .replace(ESCAPED_SLASH_MARK, "/")
        .replace(GLOB_PROTECT["!"], "!")
    )
    out: List[str] = []
    i = 0
    while i < len(protected):
        ch = protected[i]
        if ch == "[":
            j = i + 1
            cls: List[str] = []
            while j < len(protected) and protected[j] != "]":
                cls.append(protected[j])
                j += 1
            if j < len(protected) and protected[j] == "]":
                hy_count = cls.count(GLOB_PROTECT["-"])
                cls = [c for c in cls if c != GLOB_PROTECT["-"]]
                if hy_count:
                    cls.extend("-" for _ in range(hy_count))
                out.append("[")
                out.extend(cls)
                out.append("]")
                i = j + 1
                continue
        if ch == "\\" and i + 1 < len(protected):
            nxt = protected[i + 1]
            if nxt == "*":
                out.append("[*]")
            elif nxt == "?":
                out.append("[?]")
            elif nxt == "[":
                out.append("[[]")
            elif nxt == "]":
                out.append("[]]")
            else:
                out.append(nxt)
            i += 2
            continue
        if ch == GLOB_PROTECT["-"]:
            out.append("-")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def glob_pattern_display(text: str) -> str:
    return (
        text.replace(GLOB_PROTECT["*"], "*")
        .replace(GLOB_PROTECT["?"], "?")
        .replace(GLOB_PROTECT["["], "[")
        .replace(GLOB_PROTECT["]"], "]")
        .replace(GLOB_PROTECT["\\"], "\\")
        .replace(ESCAPED_SLASH_MARK, "\\/")
        .replace(GLOB_PROTECT["-"], "-")
        .replace(GLOB_PROTECT["!"], "!")
    )
