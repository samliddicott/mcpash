#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _die(msg: str) -> int:
    print(f"[FAIL] {msg}", file=sys.stderr)
    return 1


def _require_dict(obj: object, path: str) -> dict:
    if not isinstance(obj, dict):
        raise ValueError(f"{path} must be an object")
    return obj


def _require_int(obj: object, path: str) -> int:
    if not isinstance(obj, int):
        raise ValueError(f"{path} must be an integer")
    return obj


def _require_bool(obj: object, path: str) -> bool:
    if not isinstance(obj, bool):
        raise ValueError(f"{path} must be a boolean")
    return obj


def _require_str(obj: object, path: str) -> str:
    if not isinstance(obj, str) or not obj:
        raise ValueError(f"{path} must be a non-empty string")
    return obj


def validate(payload: dict) -> None:
    schema_version = _require_int(payload.get("schema_version"), "schema_version")
    if schema_version != 1:
        raise ValueError("schema_version must be 1")
    _require_str(payload.get("generator"), "generator")
    ts = _require_str(payload.get("timestamp_utc"), "timestamp_utc")
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", ts):
        raise ValueError("timestamp_utc must be ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    _require_str(payload.get("log_dir"), "log_dir")

    steps = _require_dict(payload.get("steps"), "steps")
    for step_name in ("bridge", "diff", "busybox"):
        step = _require_dict(steps.get(step_name), f"steps.{step_name}")
        _require_int(step.get("rc"), f"steps.{step_name}.rc")
        _require_bool(step.get("ok"), f"steps.{step_name}.ok")

    busybox = _require_dict(steps.get("busybox"), "steps.busybox")
    for k in (
        "summary_line",
        "skipped",
        "allowed_fail_files",
        "unexpected_fail_files",
    ):
        if k not in busybox:
            raise ValueError(f"steps.busybox.{k} is required")
    _require_bool(busybox.get("skipped"), "steps.busybox.skipped")

    overall = _require_dict(payload.get("overall"), "overall")
    _require_int(overall.get("rc"), "overall.rc")
    _require_bool(overall.get("ok"), "overall.ok")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_parity_summary.py <summary.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        return _die(f"summary file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate(payload)
    except Exception as e:
        return _die(str(e))
    print(f"[PASS] parity summary validated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
