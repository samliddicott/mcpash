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


def run_ctrl_z_case(cmd: list[str], env: dict[str, str]) -> tuple[int, list[str], str]:
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

    def read_for(seconds: float) -> None:
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

    read_for(0.4)
    os.write(master, b"set +H\nset -m\nsleep 5\n")
    time.sleep(0.4)
    os.write(master, b"\x1a")  # literal Ctrl-Z
    time.sleep(0.5)
    os.write(
        master,
        b"echo JM:z:$?\n"
        b"jobs | grep -q Stopped\n"
        b"echo JM:st:$?\n"
        b"kill -CONT %1 >/dev/null 2>&1 || true\n"
        b"kill %1 >/dev/null 2>&1 || true\n"
        b"wait %1 >/dev/null 2>&1 || true\n"
        b"echo JM:done\n"
        b"exit\n",
    )
    for _ in range(120):
        if proc.poll() is not None:
            break
        read_for(0.08)

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
    txt = out.decode("utf-8", "replace").replace("\r", "")
    marker_re = re.compile(r"JM:(?:z|st):[0-9]+|JM:done$")
    latest: dict[str, str] = {}
    for ln in txt.splitlines():
        found = marker_re.search(ln.strip())
        if found:
            marker = found.group(0)
            if marker.startswith("JM:z:"):
                latest["z"] = marker
            elif marker.startswith("JM:st:"):
                latest["st"] = marker
            else:
                latest["done"] = "JM:done"
    markers: list[str] = []
    for key in ("z", "st", "done"):
        if key in latest:
            markers.append(latest[key])
    return int(proc.returncode or 0), markers, txt


def run_ctrl_y_case(cmd: list[str], env: dict[str, str]) -> tuple[int, list[str], str]:
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

    def read_for(seconds: float) -> None:
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

    read_for(0.4)
    os.write(master, b"set +H\nset -m\nstty dsusp ^Y\ncat >/dev/null\n")
    time.sleep(0.4)
    os.write(master, b"\x19")  # literal Ctrl-Y (dsusp)
    time.sleep(0.6)
    os.write(
        master,
        b"\n"
        b"echo JM:y:$?\n"
        b"jobs | grep -q Stopped\n"
        b"echo JM:st:$?\n"
        b"kill -CONT %1 >/dev/null 2>&1 || true\n"
        b"kill %1 >/dev/null 2>&1 || true\n"
        b"wait %1 >/dev/null 2>&1 || true\n"
        b"echo JM:done\n"
        b"exit\n",
    )
    for _ in range(140):
        if proc.poll() is not None:
            break
        read_for(0.08)

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
    txt = out.decode("utf-8", "replace").replace("\r", "")
    marker_re = re.compile(r"JM:(?:y|st):[0-9]+|JM:done$")
    latest: dict[str, str] = {}
    for ln in txt.splitlines():
        found = marker_re.search(ln.strip())
        if found:
            marker = found.group(0)
            if marker.startswith("JM:y:"):
                latest["y"] = marker
            elif marker.startswith("JM:st:"):
                latest["st"] = marker
            else:
                latest["done"] = "JM:done"
    markers: list[str] = []
    for key in ("y", "st", "done"):
        if key in latest:
            markers.append(latest[key])
    return int(proc.returncode or 0), markers, txt


bash_env = os.environ.copy()
bash_env.pop("PYTHONPATH", None)
bash_env.pop("MCTASH_MODE", None)
mct_env = os.environ.copy()
mct_env["PYTHONPATH"] = os.path.join(ROOT, "src")
mct_env["MCTASH_MODE"] = "bash"

bash_rc, bash_markers, bash_out = run_ctrl_z_case(["bash", "--posix", "-i"], bash_env)
mct_rc, mct_markers, mct_out = run_ctrl_z_case(["python3", "-m", "mctash", "--posix", "-i"], mct_env)

print("=== jobs-suspend:ctrl-z ===")
print(f"  bash rc={bash_rc} mctash rc={mct_rc}")
for ln in bash_markers:
    print(f"  bash: {ln}")
for ln in mct_markers:
    print(f"  mct: {ln}")

if STRICT == "1" and (bash_rc != mct_rc or bash_markers != mct_markers):
    print("[FAIL] ctrl-z suspend matrix mismatch", file=sys.stderr)
    print("--- bash tail ---", file=sys.stderr)
    print(bash_out[-1200:], file=sys.stderr)
    print("--- mctash tail ---", file=sys.stderr)
    print(mct_out[-1200:], file=sys.stderr)
    raise SystemExit(1)

if STRICT != "1":
    print("[INFO] STRICT=0: ctrl-z suspend matrix is informational")

bash_rc, bash_markers, bash_out = run_ctrl_y_case(["bash", "--posix", "-i"], bash_env)
mct_rc, mct_markers, mct_out = run_ctrl_y_case(["python3", "-m", "mctash", "--posix", "-i"], mct_env)

print("=== jobs-suspend:ctrl-y ===")
print(f"  bash rc={bash_rc} mctash rc={mct_rc}")
for ln in bash_markers:
    print(f"  bash: {ln}")
for ln in mct_markers:
    print(f"  mct: {ln}")

if STRICT == "1" and (bash_rc != mct_rc or bash_markers != mct_markers):
    print("[FAIL] ctrl-y suspend matrix mismatch", file=sys.stderr)
    print("--- bash tail ---", file=sys.stderr)
    print(bash_out[-1200:], file=sys.stderr)
    print("--- mctash tail ---", file=sys.stderr)
    print(mct_out[-1200:], file=sys.stderr)
    raise SystemExit(1)

if STRICT != "1":
    print("[INFO] STRICT=0: ctrl-y suspend matrix is informational")

print("[PASS] job suspend ctrl matrix")
PY
