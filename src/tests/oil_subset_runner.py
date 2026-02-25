#!/usr/bin/env python3
"""Run a small subset of Oil spec tests against mctash.

This parser intentionally supports only common assertions used by the initial
POSIX-ish slices we run (status/stdout/stderr and JSON variants).
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class Case:
    name: str
    body: str = ""
    expected_status: int = 0
    expected_stdout: Optional[str] = None
    expected_stderr: Optional[str] = None
    alt_statuses: List[int] = field(default_factory=list)
    alt_stdouts: List[str] = field(default_factory=list)
    alt_stderrs: List[str] = field(default_factory=list)
    skipped_reason: Optional[str] = None
    raw_assertions: List[str] = field(default_factory=list)


def _finalize_block(lines: List[str]) -> str:
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def parse_spec(path: Path) -> List[Case]:
    cases: List[Case] = []
    current: Optional[Case] = None
    body_lines: List[str] = []
    block_mode: Optional[str] = None
    block_lines: List[str] = []

    def ensure_case() -> Case:
        nonlocal current
        if current is None:
            raise ValueError(f"Assertion before case marker in {path}")
        return current

    def finish_case() -> None:
        nonlocal current, body_lines, block_mode, block_lines
        if current is None:
            return
        if block_mode is not None:
            current.skipped_reason = (
                current.skipped_reason
                or f"unterminated assertion block {block_mode!r}"
            )
        current.body = "\n".join(body_lines).rstrip() + "\n" if body_lines else ""
        cases.append(current)
        current = None
        body_lines = []
        block_mode = None
        block_lines = []

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            if line.startswith("#### "):
                finish_case()
                current = Case(name=line[5:].strip())
                continue

            if current is None:
                continue

            if block_mode:
                if line == "## END":
                    text = _finalize_block(block_lines)
                    if block_mode == "stdout":
                        current.expected_stdout = text
                    elif block_mode == "stderr":
                        current.expected_stderr = text
                    block_mode = None
                    block_lines = []
                    continue
                if line.startswith("## "):
                    text = _finalize_block(block_lines)
                    if block_mode == "stdout":
                        current.expected_stdout = text
                    elif block_mode == "stderr":
                        current.expected_stderr = text
                    block_mode = None
                    block_lines = []
                    # Fall through and interpret this assertion line.
                else:
                    block_lines.append(line)
                    continue

            if line.startswith("## "):
                c = ensure_case()
                c.raw_assertions.append(line)
                if line.startswith("## status:"):
                    c.expected_status = int(line.split(":", 1)[1].strip())
                elif line.startswith("## stdout:"):
                    c.expected_stdout = line.split(":", 1)[1].lstrip() + "\n"
                elif line.startswith("## stderr:"):
                    c.expected_stderr = line.split(":", 1)[1].lstrip() + "\n"
                elif line.startswith("## stdout-json:"):
                    c.expected_stdout = json.loads(line.split(":", 1)[1].strip())
                elif line.startswith("## stderr-json:"):
                    c.expected_stderr = json.loads(line.split(":", 1)[1].strip())
                elif line == "## STDOUT:":
                    block_mode = "stdout"
                    block_lines = []
                elif line == "## STDERR:":
                    block_mode = "stderr"
                    block_lines = []
                elif line.startswith("## N-I") or line.startswith("## BUG"):
                    c.skipped_reason = "non-portable Oil-specific assertion annotation"
                elif line.startswith("## OK") or line.startswith("## notes:"):
                    # Some specs include shell-specific acceptable alternatives.
                    m = re.match(r"## OK [^:]+ status:\s*([0-9]+)\s*$", line)
                    if m:
                        c.alt_statuses.append(int(m.group(1)))
                    m = re.match(r"## OK [^:]+ stdout:\s*(.*)\s*$", line)
                    if m:
                        c.alt_stdouts.append(m.group(1) + "\n")
                    m = re.match(r"## OK [^:]+ stderr:\s*(.*)\s*$", line)
                    if m:
                        c.alt_stderrs.append(m.group(1) + "\n")
                    m = re.match(r"## OK [^:]+ stdout-json:\s*(.+)\s*$", line)
                    if m:
                        c.alt_stdouts.append(json.loads(m.group(1)))
                    m = re.match(r"## OK [^:]+ stderr-json:\s*(.+)\s*$", line)
                    if m:
                        c.alt_stderrs.append(json.loads(m.group(1)))
                else:
                    c.skipped_reason = f"unsupported assertion directive: {line}"
                continue

            body_lines.append(line)

    finish_case()
    return cases


def run_case(
    case: Case,
    shell_cmd: List[str],
    base_tmp: Path,
    helper_path: Optional[str],
    shell_path: Optional[str],
    workdir: Optional[str],
) -> Tuple[bool, str]:
    if case.skipped_reason:
        return True, f"SKIP {case.name}: {case.skipped_reason}"

    with tempfile.TemporaryDirectory(prefix="oil-spec-", dir=str(base_tmp)) as td:
        td_path = Path(td)
        script_path = td_path / "case.sh"
        script_path.write_text(case.body, encoding="utf-8")

        env = os.environ.copy()
        env["TMP"] = str(td_path)
        if helper_path:
            env["PATH"] = helper_path + os.pathsep + env.get("PATH", "")
        if shell_path:
            env["SH"] = shell_path

        proc = subprocess.run(
            shell_cmd + [str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=workdir,
        )

        errs: List[str] = []
        if case.expected_status == 99:
            status_ok = proc.returncode != 0
        else:
            accepted = [case.expected_status] + case.alt_statuses
            status_ok = proc.returncode in accepted
        if not status_ok:
            errs.append(
                f"status expected={case.expected_status} actual={proc.returncode}"
            )
        if case.expected_stdout is not None:
            allowed = [case.expected_stdout] + case.alt_stdouts
            if proc.stdout not in allowed:
                errs.append(
                    f"stdout mismatch expected={case.expected_stdout!r} actual={proc.stdout!r}"
                )
        if case.expected_stderr is not None:
            allowed = [case.expected_stderr] + case.alt_stderrs
            if proc.stderr not in allowed:
                errs.append(
                    f"stderr mismatch expected={case.expected_stderr!r} actual={proc.stderr!r}"
                )

        if errs:
            return False, f"FAIL {case.name}: " + "; ".join(errs)
        return True, f"PASS {case.name}"


def iter_spec_files(spec_dir: Path, names: Iterable[str]) -> List[Path]:
    paths: List[Path] = []
    for name in names:
        clean = name[:-8] if name.endswith(".test.sh") else name
        p = spec_dir / f"{clean}.test.sh"
        if not p.exists():
            raise FileNotFoundError(f"Spec file not found: {p}")
        paths.append(p)
    return paths


def make_py3_argv_helper(base_tmp: Path) -> str:
    helper_dir = tempfile.mkdtemp(prefix="mctash-oil-helpers-", dir=str(base_tmp))
    argv_path = Path(helper_dir) / "argv.py"
    argv_path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "def _py2_repr(s):\n"
        "    b = s.encode('utf-8', 'surrogateescape')\n"
        "    r = repr(b)\n"
        "    if r.startswith(\"b'\") or r.startswith('b\"'):\n"
        "        return r[1:]\n"
        "    return r\n"
        "print('[' + ', '.join(_py2_repr(a) for a in sys.argv[1:]) + ']')\n",
        encoding="utf-8",
    )
    argv_path.chmod(0o755)
    python2_path = Path(helper_dir) / "python2"
    python2_path.write_text(
        "#!/usr/bin/env bash\n"
        "exec python3 \"$@\"\n",
        encoding="utf-8",
    )
    python2_path.chmod(0o755)
    return helper_dir


def make_shell_wrapper(base_tmp: Path, shell_cmd: List[str]) -> str:
    wrapper_dir = tempfile.mkdtemp(prefix="mctash-shell-wrapper-", dir=str(base_tmp))
    wrapper_path = Path(wrapper_dir) / "sh"
    wrapper_path.write_text(
        "#!/usr/bin/env bash\n"
        f"exec {shlex.join(shell_cmd)} \"$@\"\n",
        encoding="utf-8",
    )
    wrapper_path.chmod(0o755)
    return str(wrapper_path)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec-root", required=True)
    ap.add_argument(
        "--shell-cmd",
        default="python3 -m mctash",
        help="Command used to execute each case script",
    )
    ap.add_argument(
        "--max-cases",
        type=int,
        default=0,
        help="If > 0, cap number of cases per file",
    )
    ap.add_argument(
        "--helper-path",
        default="",
        help="Optional directory prepended to PATH for test helpers like argv.py",
    )
    ap.add_argument(
        "--workdir",
        default="",
        help="Optional working directory used when executing test cases",
    )
    ap.add_argument("spec_names", nargs="+")
    ns = ap.parse_args(argv)

    spec_root = Path(ns.spec_root)
    files = iter_spec_files(spec_root, ns.spec_names)
    shell_cmd = ns.shell_cmd.split()
    base_tmp = Path(tempfile.gettempdir())
    shim_dir = make_py3_argv_helper(base_tmp)
    shell_wrapper = make_shell_wrapper(base_tmp, shell_cmd)
    helper_path = shim_dir
    if ns.helper_path:
        helper_path = helper_path + os.pathsep + ns.helper_path

    total = passed = failed = skipped = 0
    for p in files:
        cases = parse_spec(p)
        if ns.max_cases > 0:
            cases = cases[: ns.max_cases]
        print(f"# {p.name} ({len(cases)} cases)")
        for c in cases:
            total += 1
            ok, msg = run_case(c, shell_cmd, base_tmp, helper_path, shell_wrapper, ns.workdir or None)
            if c.skipped_reason:
                skipped += 1
            elif ok:
                passed += 1
            else:
                failed += 1
            print(msg)

    print(f"SUMMARY total={total} pass={passed} fail={failed} skip={skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
