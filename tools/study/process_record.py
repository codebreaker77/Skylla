"""Preserve process evidence without interpreting shell status as bug status."""

import json
import subprocess
import time


def decode(value):
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else (value or "")


def execute(argv, cwd=None, env=None, timeout=30):
    started = time.perf_counter()
    record = {"argv": list(argv), "cwd": str(cwd) if cwd else None}
    try:
        result = subprocess.run(argv, cwd=cwd, env=env, timeout=timeout,
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr,
                      timed_out=False, launch_error=None)
    except subprocess.TimeoutExpired as exc:
        record.update(returncode=None, stdout=decode(exc.stdout), stderr=decode(exc.stderr),
                      timed_out=True, launch_error=None)
    except OSError as exc:
        record.update(returncode=None, stdout="", stderr="", timed_out=False,
                      launch_error={"type": type(exc).__name__, "message": str(exc)})
    record["elapsed_seconds"] = time.perf_counter() - started
    try:
        record["payload"] = json.loads(record["stdout"])
        record["payload_error"] = None
    except ValueError as exc:
        record["payload"] = None
        record["payload_error"] = type(exc).__name__
    return record


def readiness(record, expected_case):
    payload = record.get("payload")
    return (record.get("returncode") == 0 and not record.get("timed_out")
            and record.get("launch_error") is None and isinstance(payload, dict)
            and payload.get("case") == expected_case and payload.get("ready") is True
            and payload.get("imported_pinned_source") is True)
