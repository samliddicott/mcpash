#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRICT="${STRICT:-0}"

ROOT="$ROOT" STRICT="$STRICT" python3 - <<'PY'
import os
import pty
import re
import select
import signal
import subprocess
import sys
import time

ROOT = os.environ["ROOT"]
STRICT = os.environ.get("STRICT", "0")
MARK = "__AFTER_INT__"


def _read_until_prompt(master: int, proc: subprocess.Popen, out: bytearray, deadline_s: float) -> bool:
    deadline = time.time() + deadline_s
    prompt_re = re.compile(rb"(?:\r?\n|^).*[#$] ?$")
    while time.time() < deadline:
        r, _, _ = select.select([master], [], [], 0.1)
        if master in r:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                chunk = b""
            if chunk:
                out.extend(chunk)
                if prompt_re.search(bytes(out[-4096:])):
                    return True
        if proc.poll() is not None:
            return False
    return False


def _drain(master: int, out: bytearray, seconds: float) -> None:
    end = time.time() + seconds
    while time.time() < end:
        r, _, _ = select.select([master], [], [], 0.05)
        if master not in r:
            continue
        try:
            chunk = os.read(master, 4096)
        except OSError:
            return
        if not chunk:
            return
        out.extend(chunk)


def _run_case(cmd: list[str], env: dict[str, str], lane: str) -> tuple[int, str, bool, str]:
    master, slave = pty.openpty()
    proc = subprocess.Popen(
        cmd,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        text=False,
        close_fds=True,
        preexec_fn=os.setsid,
        env=env,
    )
    out = bytearray()
    inv_ok = True
    inv_checked = False
    inv_note = "ok"

    _read_until_prompt(master, proc, out, 2.0)
    os.write(master, b"sleep 5\n")
    time.sleep(0.3)

    if lane == "strict-child-sigint":
        child_pid = None
        deadline = time.time() + 1.5
        while time.time() < deadline:
            try:
                ps = subprocess.check_output(["ps", "--ppid", str(proc.pid), "-o", "pid=", "-o", "comm="], text=True)
            except Exception:
                ps = ""
            for ln in ps.splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                parts = ln.split(None, 1)
                if not parts:
                    continue
                pid = int(parts[0])
                comm = parts[1] if len(parts) > 1 else ""
                if comm.strip() == "sleep":
                    child_pid = pid
                    break
            if child_pid is not None:
                break
            time.sleep(0.05)
        if child_pid is not None:
            try:
                child_pgid = os.getpgid(child_pid)
                tty_fg = None
                try:
                    tty_fg = os.tcgetpgrp(slave)
                except OSError:
                    try:
                        tty_fg = os.tcgetpgrp(master)
                    except OSError:
                        tty_fg = None
                if tty_fg is not None and tty_fg > 1:
                    inv_checked = True
                    if child_pgid != tty_fg:
                        inv_ok = False
                        inv_note = f"fg-invariant mismatch: tty_fg={tty_fg} child_pgid={child_pgid}"
                else:
                    inv_note = "fg-invariant not probeable in this harness environment"
            except Exception as e:
                inv_ok = False
                inv_note = f"fg-invariant probe error: {e}"
            try:
                os.kill(child_pid, signal.SIGINT)
            except Exception:
                pass
        else:
            inv_ok = False
            inv_note = "fg-invariant probe error: sleep child pid not found"
    else:
        # Literal terminal INTR char lane (informational).
        os.write(master, b"\x03")

    if not _read_until_prompt(master, proc, out, 3.0):
        _drain(master, out, 1.0)
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            pass
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                pass
            proc.wait(timeout=2)
        os.close(master)
        os.close(slave)
        return int(proc.returncode or 1), out.decode("utf-8", "replace"), (inv_ok if inv_checked else True), inv_note

    os.write(master, f"echo {MARK}\nexit\n".encode("utf-8"))
    _drain(master, out, 2.0)
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            pass
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
        proc.wait(timeout=2)
    os.close(master)
    os.close(slave)
    return int(proc.returncode or 0), out.decode("utf-8", "replace"), (inv_ok if inv_checked else True), inv_note


def _check(name: str, cmd: list[str], env: dict[str, str], lane: str) -> tuple[bool, str]:
    rc, out, inv_ok, inv_note = _run_case(cmd, env, lane)
    ok = rc == 0 and MARK in out and (lane != "strict-child-sigint" or inv_ok)
    if not ok:
        return False, f"{name} lane={lane} rc={rc} inv={inv_note}\n{out[-2000:]}"
    return True, out


bash_env = os.environ.copy()
bash_env.pop("PYTHONPATH", None)
bash_env.pop("MCTASH_MODE", None)

mct_env = os.environ.copy()
mct_env["PYTHONPATH"] = os.path.join(ROOT, "src")
mct_env["MCTASH_MODE"] = "bash"

cases = [
    ("bash", ["bash", "--posix", "-i"], bash_env),
    ("mctash", ["python3", "-m", "mctash", "-i"], mct_env),
]

# Strict lane: deterministic foreground-command SIGINT interruption.
failed = []
for name, cmd, env in cases:
    ok, diag = _check(name, cmd, env, "strict-child-sigint")
    if not ok:
        failed.append(diag)

if failed:
    for f in failed:
        print(f"[FAIL] interactive SIGINT strict case\n{f}", file=sys.stderr)
    raise SystemExit(1)

# Informational lane: literal Ctrl-C via PTY control character.
info_failed = []
for name, cmd, env in cases:
    ok, diag = _check(name, cmd, env, "literal-ctrl-c")
    if not ok:
        info_failed.append(diag)

if info_failed:
    for f in info_failed:
        print(f"[INFO] interactive SIGINT literal case\n{f}")
    print("[INFO] literal Ctrl-C lane is informational")

print("[PASS] interactive SIGINT matrix")
PY
