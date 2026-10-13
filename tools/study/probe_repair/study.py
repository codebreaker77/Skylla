"""Freeze, run, and verify the controlled probe-repair development study."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import tempfile
import time

from fixtures import CONDITIONS, FAMILIES
from policies import ARMS

ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "experiments/probe-repair"
FROZEN = STUDY / "protocol.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def freeze():
    if FROZEN.exists():
        raise ValueError("Protocol already frozen; preserve it and version any new study")
    sources = [STUDY / "METHODOLOGY.md", ROOT / "tests/test_probe_repair_apparatus.py"]
    sources += sorted((STUDY / "programs").glob("*.py"))
    sources += sorted(Path(__file__).parent.glob("*.py"))
    protocol = {"schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                "study": "Controlled probe-repair development study, v1",
                "families": list(FAMILIES), "conditions": list(CONDITIONS),
                "fault_states": [True, False], "arms": list(ARMS), "seeds": [101, 202, 303],
                "target_invocation_budget": 8, "calibration_cost": 3,
                "episode_timeout_seconds": 15, "schedule_seed": 417,
                "expected_episodes": len(FAMILIES) * len(CONDITIONS) * 2 * len(ARMS) * 3,
                "source_hashes": {path.relative_to(ROOT).as_posix(): digest(path) for path in sources}}
    write_json(FROZEN, protocol)
    print("Frozen", protocol["expected_episodes"], "episodes at", FROZEN)


def load_protocol():
    protocol = json.loads(FROZEN.read_text(encoding="utf-8"))
    for path, expected in protocol["source_hashes"].items():
        if digest(ROOT / path) != expected:
            raise ValueError("Frozen source changed: " + path)
    return protocol


def requests(protocol):
    return [{"family": family, "condition": condition, "fault_present": fault,
             "seed": seed, "arm": arm, "budget": protocol["target_invocation_budget"]}
            for family, condition, fault, seed, arm in itertools.product(
                protocol["families"], protocol["conditions"], protocol["fault_states"],
                protocol["seeds"], protocol["arms"])]


def identity(request):
    return "__".join(str(request[key]) for key in ("family", "condition", "fault_present", "seed", "arm"))


def run_one(request, timeout, raw_dir):
    work_root = ROOT / "workspaces/probe-repair"
    work_root.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="episode-", dir=work_root))
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC") if key in os.environ}
    env.update({"HOME": str(work), "USERPROFILE": str(work), "TEMP": str(work), "TMP": str(work),
                "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                "PYTHONIOENCODING": "utf-8"})
    command = [sys.executable, str(Path(__file__).parent / "episode.py")]
    start = time.perf_counter()
    try:
        process = subprocess.run(command, input=json.dumps(request), cwd=work, env=env,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        stdout, stderr, code = process.stdout, process.stderr, process.returncode
        try:
            episode = json.loads(stdout) if code == 0 else None
        except ValueError as error:
            episode = None
            stderr += "\nEpisode JSON parsing failed: " + str(error)
        status = "completed" if episode is not None else "infrastructure_failure"
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
        stdout, stderr, code, episode, status = decode(error.stdout), decode(error.stderr), None, None, "timeout"
    except OSError as error:
        stdout, stderr, code, episode, status = "", str(error), None, None, "infrastructure_failure"
    seconds = time.perf_counter() - start
    raw = raw_dir / (identity(request) + ".json")
    write_json(raw, {"request": request, "argv": command, "cwd": str(work),
                     "stdout": stdout, "stderr": stderr, "exit_code": code})
    return {"id": identity(request), "request": request, "status": status, "episode": episode,
            "subprocess_wall_seconds": seconds, "raw_log": raw.relative_to(ROOT).as_posix(),
            "raw_log_sha256": digest(raw)}


def aggregate(records, protocol):
    arms, by_condition = {}, {}
    for arm in protocol["arms"]:
        selected = [record for record in records if record["request"]["arm"] == arm]
        positives = [record for record in selected if record["request"]["fault_present"]]
        negatives = [record for record in selected if not record["request"]["fault_present"]]
        episodes = [record["episode"] for record in selected if record["episode"] is not None]
        positive_episodes = [record["episode"] for record in positives if record["episode"] is not None]
        arms[arm] = {
            "positive_episodes": len(positives),
            "verified_discriminators": sum(episode["verified_discriminator"] for episode in positive_episodes),
            "negative_episodes": len(negatives),
            "false_completions": sum(episode["false_completion"] for episode in episodes),
            "completed_episodes": len(episodes), "target_invocations": sum(episode["invocations"] for episode in episodes),
            "mean_invocations_completed": sum(episode["invocations"] for episode in episodes) / len(episodes) if episodes else None,
            "mean_invocations_positive": sum(episode["invocations"] for episode in positive_episodes) / len(positive_episodes) if positive_episodes else None,
            "calibration_invocations": sum(sum(entry["kind"].startswith("calibration_") for entry in episode["trace"]) for episode in episodes),
            "reference_invocations": sum(episode["reference_invocations"] for episode in episodes),
            "masked_positive_controls_passed": sum(control["sensitive"] for episode in episodes if episode["fault_present"] and episode["condition"] == "masked_result" for control in episode["controls"]),
            "sum_subprocess_wall_seconds": sum(record["subprocess_wall_seconds"] for record in selected),
        }
        by_condition[arm] = {}
        for condition in protocol["conditions"]:
            subset = [record for record in positives if record["request"]["condition"] == condition]
            by_condition[arm][condition] = {"episodes": len(subset),
                "verified": sum(bool(record["episode"] and record["episode"]["verified_discriminator"]) for record in subset)}
    return {"arms": arms, "positive_results_by_condition": by_condition,
            "records": len(records), "completed": sum(record["status"] == "completed" for record in records),
            "failures": [record["id"] for record in records if record["status"] != "completed"]}


def run(name, workers):
    protocol = load_protocol()
    if not name or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for char in name):
        raise ValueError("Use a lowercase simple run name")
    output = STUDY / "results" / name
    output.mkdir(parents=True, exist_ok=False)
    raw_dir = ROOT / "artifacts/probe-repair" / name
    raw_dir.mkdir(parents=True, exist_ok=False)
    order = requests(protocol)
    random.Random(protocol["schedule_seed"]).shuffle(order)
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    records = []
    with (output / "episodes.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(run_one, request, protocol["episode_timeout_seconds"], raw_dir) for request in order]
            for future in as_completed(futures):
                record = future.result()
                records.append(record)
                stream.write(json.dumps(record, separators=(",", ":")) + "\n")
                stream.flush()
                if len(records) % 100 == 0:
                    print("Recorded", len(records), "/", len(order), flush=True)
    summary = aggregate(records, protocol)
    summary.update({"started_at_utc": started_at, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                    "elapsed_wall_seconds": time.perf_counter() - start, "python": sys.version,
                    "platform": platform.platform(), "workers": workers,
                    "protocol_sha256": digest(FROZEN), "episodes_sha256": digest(output / "episodes.jsonl"),
                    "purpose": "Controlled development mechanism study, no model or agent repair evaluation"})
    write_json(output / "summary.json", summary)
    print(json.dumps(summary["arms"], indent=2))


def verify(name):
    protocol = load_protocol()
    output = STUDY / "results" / name
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    if summary["protocol_sha256"] != digest(FROZEN) or summary["episodes_sha256"] != digest(output / "episodes.jsonl"):
        raise ValueError("Changed run artifacts")
    records = [json.loads(line) for line in (output / "episodes.jsonl").read_text(encoding="utf-8").splitlines()]
    expected = {identity(request) for request in requests(protocol)}
    if len(records) != len(expected) or {record["id"] for record in records} != expected:
        raise ValueError("Missing or duplicated episodes")
    if any(summary[key] != value for key, value in aggregate(records, protocol).items()):
        raise ValueError("Aggregate differs from episode records")
    raw_count, workspaces = 0, set()
    for record in records:
        raw = (ROOT / record["raw_log"]).resolve()
        if not raw.is_relative_to((ROOT / "artifacts/probe-repair").resolve()):
            raise ValueError("Unexpected raw-log path")
        if raw.exists():
            if digest(raw) != record["raw_log_sha256"]:
                raise ValueError("Raw log changed")
            payload = json.loads(raw.read_text(encoding="utf-8"))
            if payload["cwd"] in workspaces:
                raise ValueError("Episode workspace reused")
            workspaces.add(payload["cwd"])
            if record["episode"] is not None and json.loads(payload["stdout"]) != record["episode"]:
                raise ValueError("Parsed episode differs from stdout")
            raw_count += 1
        episode = record["episode"]
        if episode is not None:
            if episode["invocations"] != len(episode["trace"]) or episode["invocations"] > protocol["target_invocation_budget"]:
                raise ValueError("Budget accounting mismatch")
            if [entry["invocation"] for entry in episode["trace"]] != list(range(1, episode["invocations"] + 1)):
                raise ValueError("Invalid invocation sequence")
            normal = {entry["invocation"] for entry in episode["trace"] if entry["kind"] == "probe"}
            if {entry["invocation"] for entry in episode["evaluation"]} != normal:
                raise ValueError("Calibration counted as diagnosis or probe left unevaluated")
    print("Verified", len(records), "episodes and", raw_count, "available raw logs; aggregate and budgets match")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("freeze", "run", "verify"))
    parser.add_argument("--name", default="run-001")
    parser.add_argument("--workers", type=int, choices=(1, 2, 3), default=3)
    args = parser.parse_args()
    if args.operation == "freeze":
        freeze()
    elif args.operation == "run":
        run(args.name, args.workers)
    else:
        verify(args.name)
