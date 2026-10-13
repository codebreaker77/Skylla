"""Frozen local CUDA shadow decisions; no code edits, hosted judge or repair claims."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from judge_baseline import evaluate, OPTIONS, canonical
from laya_backend import create_model

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/judge-baseline"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def main(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Unsafe run name")
    output = CONFIG / "results" / name
    output.mkdir(parents=True, exist_ok=False)
    paths = sorted((CONFIG / "states").glob("*.json"))
    states = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    if len(states) != 3:
        raise ValueError("Expected the three frozen exposed development examples")
    orders = {"original": list(OPTIONS), "reversed": list(reversed(OPTIONS))}
    protocol = {"schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                "scope": "Three exposed development states; no gold action labels, repair outcomes or accuracy estimate",
                "state_files_sha256": {p.name: sha(p) for p in paths}, "orders": orders,
                "repetitions": 2, "warmup_calls": 1, "required_device": "cuda", "dtype": "float16",
                "max_len": 1024, "head_max_len": 256,
                "method_sha256": sha(CONFIG / "METHODOLOGY.md"), "checkpoint_sha256": sha(CONFIG / "laya-checkpoint.json"),
                "implementation_sha256": {p: sha(ROOT / p) for p in ("tools/study/judge_baseline.py", "tools/study/laya_backend.py", "tools/study/run_laya_shadow.py")}}
    write(output / "protocol.json", protocol)
    started = time.perf_counter()
    try:
        model = create_model(ROOT / "artifacts/laya-baseline/checkpoint")
    except Exception as exc:
        write(output / "summary.json", {"status": "model_load_failure", "error_type": type(exc).__name__,
                                       "message": str(exc), "elapsed_seconds": time.perf_counter() - started,
                                       "protocol_sha256": sha(output / "protocol.json")})
        raise
    # Record the initial cold decision separately; retain it even on failure.
    warmup = evaluate(states[0], "deepeval-laya", model.get_model_name(), model)
    write(output / "warmup.json", warmup)
    records = []
    for repetition in range(2):
        for order_name, order in orders.items():
            for state in states:
                record = evaluate(state, "deepeval-laya", model.get_model_name(), model, order)
                record.update(repetition=repetition, order_name=order_name)
                records.append(record)
                write(output / "decisions.json", records)
                print(state["state_id"], order_name, record["status"], (record["recommendation"] or {}).get("action"), flush=True)
    flips, instability = [], []
    for state in states:
        for repetition in range(2):
            pair = [r for r in records if r["state"]["state_id"] == state["state_id"] and r["repetition"] == repetition]
            completed = all(r["status"] == "completed" for r in pair)
            flips.append({"state_id": state["state_id"], "repetition": repetition, "comparable": completed,
                          "different": pair[0]["recommendation"]["action"] != pair[1]["recommendation"]["action"] if completed else None})
        for order in orders:
            pair = [r for r in records if r["state"]["state_id"] == state["state_id"] and r["order_name"] == order]
            completed = all(r["status"] == "completed" for r in pair)
            instability.append({"state_id": state["state_id"], "order_name": order, "comparable": completed,
                                "different": pair[0]["recommendation"]["action"] != pair[1]["recommendation"]["action"] if completed else None})
    write(output / "summary.json", {"status": "completed_apparatus_run", "decisions": len(records),
                                   "completed_decisions": sum(r["status"] == "completed" for r in records),
                                   "model_load_seconds": model.load_seconds, "hardware": model.hardware,
                                   "warmup_status": warmup["status"], "order_comparisons": flips, "repeat_comparisons": instability,
                                   "protocol_sha256": sha(output / "protocol.json"), "decisions_sha256": sha(output / "decisions.json"),
                                   "warmup_sha256": sha(output / "warmup.json"), "elapsed_seconds": time.perf_counter() - started,
                                   "package_inventory": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
                                   "scope": protocol["scope"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="laya-gpu-001")
    main(parser.parse_args().name)
