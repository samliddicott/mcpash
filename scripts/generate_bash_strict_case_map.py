#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


def scenario_cases_for_req(req_id: str) -> list[str]:
    # Invocation option matrix concrete scenarios currently implemented.
    inv = {
        "C1.OPT.SHORT.c": ["case:invocation.short-c"],
        "C1.OPT.SHORT.i": ["case:invocation.short-i"],
        "C1.OPT.SHORT.l": ["case:invocation.short-l"],
        "C1.OPT.SHORT.r": ["case:invocation.short-r"],
        "C1.OPT.SHORT.s": ["case:invocation.short-s-with-args"],
        "C1.OPT.SHORT.v": ["case:invocation.short-v"],
        "C1.OPT.SHORT.x": ["case:invocation.short-x"],
        "C1.OPT.SHORT.D": ["case:invocation.short-D"],
        "C1.OPT.SHORT.O": ["case:invocation.short-O"],
        "C1.OPT.SHORT.PLUSO": ["case:invocation.short-plusO"],
        "C1.OPT.SHORT.DASHDASH": ["case:invocation.short-dashdash"],
        "C1.OPT.SHORT.SINGLEDASH": ["case:invocation.short-singledash"],
        "C1.OPT.LONG.HELP": ["case:invocation.long-help"],
        "C1.OPT.LONG.LOGIN": ["case:invocation.long-login"],
        "C1.OPT.LONG.NOEDITING": ["case:invocation.long-noediting"],
        "C1.OPT.LONG.NOPROFILE": ["case:invocation.long-noprofile"],
        "C1.OPT.LONG.NORC": ["case:invocation.long-norc"],
        "C1.OPT.LONG.POSIX": ["case:invocation.long-posix"],
        "C1.OPT.LONG.RESTRICTED": ["case:invocation.long-restricted"],
        "C1.OPT.LONG.VERBOSE": ["case:invocation.long-verbose"],
        "C1.OPT.LONG.VERSION": ["case:invocation.long-version"],
        "C1.OPT.LONG.DUMP_STRINGS": ["case:invocation.long-dump-strings"],
        "C1.OPT.LONG.DUMP_PO_STRINGS": ["case:invocation.long-dump-po"],
        "C1.OPT.LONG.INIT_FILE_FILE": ["case:invocation.long-init-file-file"],
        "C1.OPT.LONG.RCFILE_FILE": ["case:invocation.long-rcfile-file"],
    }
    if req_id in inv:
        return inv[req_id]

    startup = {
        "C1.STARTUP.01": ["case:startup.default-bash-mode"],
        "C1.STARTUP.02": ["case:startup.explicit-posix"],
        "C1.STARTUP.03": ["case:startup.bash-env-preload"],
        "C1.STARTUP.04": ["case:startup.arg0-sh-posix"],
        "C1.STARTUP.05": ["case:startup.explicit-posix", "case:startup.arg0-sh-posix"],
        "C1.STARTUP.06": ["case:startup.restricted-startup"],
    }
    if req_id in startup:
        return startup[req_id]

    interactive = {
        "C7.INT.01": ["case:interactive.prompt-escapes"],
        "C7.INT.02": ["case:interactive.prompt-command"],
        "C7.INT.03": ["case:interactive.readline-mode"],
        "C7.INT.10": ["case:interactive.interactive-comments"],
        "C7.INT.11": ["case:interactive.prompt-expansion"],
        "C7.INT.07.FC": ["case:interactive.fc-flow"],
    }
    if req_id in interactive:
        return interactive[req_id]

    jobs = {
        "C8.JOB.13": ["case:interactive-sigint.strict-child-sigint"],
        "C8.JOB.16": ["case:jobs.fg-basic", "case:jobs.bg-basic"],
        "C8.JOB.18": ["case:job-tty-stop.ttin"],
        "C8.JOB.19": ["case:job-tty-stop.ttou"],
        "C8.JOB.20": ["case:jobs-suspend.ctrl-z"],
        "C8.JOB.25": ["case:jobs-notify.defer-vs-set-b"],
        "C8.JOB.27": ["case:jobs-exitwarn.warn-once"],
        "C8.JOB.28": ["case:jobs.wait-state-change"],
        "C8.JOB.29": ["case:jobs.wait-f-termination"],
    }
    if req_id in jobs:
        return jobs[req_id]

    return []


def main() -> int:
    matrix = Path("docs/specs/bash-man-implementation-matrix.tsv")
    out = Path("docs/specs/bash-man-strict-case-map.tsv")

    rows = list(csv.DictReader(matrix.open(newline=""), delimiter="\t"))
    by_req = {}
    for row in rows:
        by_req[row["req_id"]] = row

    with out.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["req_id", "strict_case_id", "runner", "notes"])
        for req_id in sorted(by_req):
            row = by_req[req_id]
            tests = [t.strip() for t in row["tests"].split(",") if t.strip()]
            explicit = [t for t in tests if not t.startswith("run_")]
            runners = [t for t in tests if t.startswith("run_")]
            if explicit:
                for c in explicit:
                    w.writerow([req_id, f"case:{c}", "", "case id strict assertion"])
                continue

            mapped = scenario_cases_for_req(req_id)
            if mapped:
                for c in mapped:
                    w.writerow([req_id, c, "", "runner decomposed to concrete strict scenario id"])
                continue

            if runners:
                for rn in runners:
                    note = "runner asserts req-specific checks in strict mode when available"
                    if req_id in {"C8.JOB.13", "C8.JOB.17", "C8.JOB.20", "C8.JOB.21"}:
                        note = "runner has strict deterministic lane; literal control-char lane remains informational"
                    w.writerow([req_id, f"runner:{rn}#{req_id}", rn, note])
                continue

            w.writerow([req_id, f"unmapped:{req_id}", "", "no tests listed"])
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
