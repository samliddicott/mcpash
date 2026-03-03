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


def protect_glob_meta(s: str) -> str:
    return "".join(GLOB_PROTECT.get(ch, ch) for ch in s)


def unprotect_glob_meta(s: str) -> str:
    return "".join(GLOB_UNPROTECT.get(ch, "/" if ch == ESCAPED_SLASH_MARK else ch) for ch in s)


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
