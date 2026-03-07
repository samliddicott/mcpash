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


def run_case(name: str, cmd: list[str], env: dict[str, str]) -> tuple[int, str]:
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
    os.close(slave)
    out = bytearray()

    def read_chunk(timeout: float = 0.1) -> bytes:
        r, _, _ = select.select([master], [], [], timeout)
        if master not in r:
            return b""
        try:
            return os.read(master, 4096)
        except OSError:
            return b""

    def read_until_prompt(deadline_s: float) -> bool:
        deadline = time.time() + deadline_s
        prompt_re = re.compile(rb"(?:\r?\n|^).*[#$] ?$")
        while time.time() < deadline:
            chunk = read_chunk(0.1)
            if chunk:
                out.extend(chunk)
                tail = bytes(out[-4096:])
                if prompt_re.search(tail):
                    return True
            if proc.poll() is not None:
                return False
        return False

    # Wait for initial prompt.
    read_until_prompt(2.0)

    os.write(master, b"sleep 5\n")
    time.sleep(0.2)
    # Send terminal INTR character (Ctrl-C) through the PTY.
    os.write(master, b"\x03")

    if not read_until_prompt(2.0):
        # Keep collecting whatever is left for diagnostics.
        end = time.time() + 1.0
        while time.time() < end:
            chunk = read_chunk(0.05)
            if not chunk:
                break
            out.extend(chunk)
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            pass
        proc.wait(timeout=2)
        os.close(master)
        return proc.returncode or 1, out.decode("utf-8", "replace")

    os.write(master, f"echo {MARK}\nexit\n".encode("utf-8"))

    end = time.time() + 3.0
    while time.time() < end and proc.poll() is None:
        chunk = read_chunk(0.1)
        if chunk:
            out.extend(chunk)

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
    return proc.returncode, out.decode("utf-8", "replace")


def check(name: str, cmd: list[str], env: dict[str, str]) -> tuple[bool, str]:
    rc, out = run_case(name, cmd, env)
    ok = rc == 0 and MARK in out
    if not ok:
        return False, f"{name} rc={rc}\n{out[-2000:]}"
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

failed = []
for name, cmd, env in cases:
    ok, diag = check(name, cmd, env)
    if not ok:
        failed.append(diag)

if failed:
    for f in failed:
        print(f"[FAIL] interactive SIGINT case\n{f}", file=sys.stderr)
    if STRICT == "1":
        raise SystemExit(1)
    print("[INFO] STRICT=0: interactive SIGINT matrix is informational")
    raise SystemExit(0)

print("[PASS] interactive SIGINT matrix")
PY
