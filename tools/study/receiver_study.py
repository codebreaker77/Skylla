"""Freeze and replay a development receiver filter without changing prior studies."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

from observer_study import ROOT, source, cases, fingerprint, workspace, sha, write
from process_record import execute, readiness
from receiver_filter import filter_candidates

CONFIG = ROOT / "experiments/receiver-filter"
PRIOR = ROOT / "experiments/observer-discovery"
FILES = ["tools/study/receiver_filter.py", "tools/study/receiver_study.py",
         "tools/study/observer_probe.py", "tools/study/observer_study.py",
         "tools/study/process_record.py", "tools/pilot/prepare.py", "tools/pilot/run.py"]


def freeze():
    if (CONFIG / "protocol.json").exists():
        raise ValueError("Already frozen")
    case = next(c for c in cases() if c["id"] == "tornado-6")
    path, metadata = source(case, "buggy")
    prior = json.loads((PRIOR / "protocol.json").read_text(encoding="utf-8"))
    identity = fingerprint(path)
    if identity != prior["source_identities"][case["id"]]["source_sha256"]:
        raise ValueError("Changed proposal source")
    started = time.perf_counter()
    record = execute([sys.executable, str(ROOT / "tools/study/receiver_filter.py"),
                      "--source", str(path), "--module", "tornado.platform.asyncio", "--class-name", "AsyncIOLoop"], timeout=30)
    if not readiness(record, case["id"]):
        write(CONFIG / "freeze-failure.json", record)
        raise ValueError("Receiver inspection failed; raw evidence preserved")
    proposals = json.loads((PRIOR / "proposals.json").read_text(encoding="utf-8"))["candidates"]
    kept, decisions = filter_candidates(path, proposals, record["payload"]["mro"])
    for arm, candidates in (("unfiltered", proposals), ("receiver_filtered", kept)):
        write(CONFIG / (arm + ".json"), {"schema_version": 1, "candidates": candidates})
    write(CONFIG / "filter-decisions.json", {"receiver_inspection": record, "decisions": decisions,
                                            "filter_and_receiver_seconds": time.perf_counter() - started})
    previous = json.loads((PRIOR / "results/run-001/processes.json").read_text(encoding="utf-8"))
    identities = {r["variant"]: r["source_sha256"] for r in previous if r["case"] == "tornado-6"}
    write(CONFIG / "protocol.json", {"schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                                     "case": case, "source_identities": identities, "repetitions": 3,
                                     "cycles": [1, 10], "arms": ["unfiltered", "receiver_filtered"],
                                     "implementation_sha256": {p: sha(ROOT / p) for p in FILES},
                                     "inputs_sha256": {p: sha(CONFIG / p) for p in ("METHODOLOGY.md", "unfiltered.json", "receiver_filtered.json", "filter-decisions.json")},
                                     "prior_proposals_sha256": sha(PRIOR / "proposals.json")})
    print("Frozen receiver filter:", len(proposals), "to", len(kept), "fields")


def validate():
    protocol = json.loads((CONFIG / "protocol.json").read_text(encoding="utf-8"))
    for relative, expected in protocol["implementation_sha256"].items():
        if sha(ROOT / relative) != expected:
            raise ValueError("Changed implementation: " + relative)
    for relative, expected in protocol["inputs_sha256"].items():
        if sha(CONFIG / relative) != expected:
            raise ValueError("Changed frozen input: " + relative)
    return protocol


def run(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Unsafe run name")
    protocol = validate()
    output = CONFIG / "results" / name
    output.mkdir(parents=True, exist_ok=False)
    records = []
    start = time.perf_counter()
    case = protocol["case"]
    for variant in ("buggy", "fixed"):
        path, metadata = source(case, variant)
        identity = fingerprint(path)
        if identity != protocol["source_identities"][variant]:
            raise ValueError("Changed reference/proposal source")
        for repetition in range(protocol["repetitions"]):
            for arm in protocol["arms"]:
                for cycles in protocol["cycles"]:
                    work, env = workspace(path, case)
                    record = execute([sys.executable, str(ROOT / "tools/study/observer_probe.py"), "--case", case["id"],
                                      "--arm", "source_containers", "--cycles", str(cycles), "--candidates", str(CONFIG / (arm + ".json"))], work, env, timeout=30)
                    record.update(variant=variant, repetition=repetition, arm=arm, cycles=cycles,
                                  source_sha256=identity, commit=metadata["commit"])
                    records.append(record)
                    write(output / "processes.json", records)
                    print(variant, arm, cycles, record["returncode"], flush=True)
    pairs = []
    for repetition in range(protocol["repetitions"]):
        for arm in protocol["arms"]:
            for cycles in protocol["cycles"]:
                matching = [r for r in records if (r["repetition"], r["arm"], r["cycles"]) == (repetition, arm, cycles)]
                valid = len(matching) == 2 and all(r["returncode"] == 0 and isinstance(r["payload"], dict)
                    and r["payload"].get("case") == case["id"] and r["payload"].get("imported_pinned_source") is True for r in matching)
                observations = [r["payload"]["observation"] for r in matching] if valid else []
                pairs.append({"repetition": repetition, "arm": arm, "cycles": cycles,
                              "comparable": valid, "different": observations[0] != observations[1] if valid else None})
    accesses = {}
    for arm in protocol["arms"]:
        readings = [v for r in records if r["arm"] == arm and isinstance(r["payload"], dict)
                    for obs in [r["payload"].get("observation", {})]
                    for snapshot in [obs.get("before", {}), obs.get("after", {})] + [s for e in obs.get("events", []) for s in (e["active"], e["closed"])]
                    for v in snapshot.values()]
        accesses[arm] = {"total": len(readings), "unavailable": sum(v["status"] == "unavailable" for v in readings)}
    write(output / "summary.json", {"schema_version": 1, "scope": "One exposed development bug; no repairs or models",
                                   "python": sys.version, "processes": len(records), "pairs": pairs,
                                   "field_accesses": accesses, "process_elapsed_seconds": sum(r["elapsed_seconds"] for r in records),
                                   "runner_elapsed_seconds": time.perf_counter() - start,
                                   "protocol_sha256": sha(CONFIG / "protocol.json"), "processes_sha256": sha(output / "processes.json")})


def verify(name):
    validate()
    output = CONFIG / "results" / name
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    if summary["protocol_sha256"] != sha(CONFIG / "protocol.json") or summary["processes_sha256"] != sha(output / "processes.json"):
        raise ValueError("Changed run artifact")
    records = json.loads((output / "processes.json").read_text(encoding="utf-8"))
    if len(records) != summary["processes"]:
        raise ValueError("Count mismatch")
    expected = {(v, r, a, c) for v in ("buggy", "fixed") for r in range(3)
                for a in ("unfiltered", "receiver_filtered") for c in (1, 10)}
    identities = [(r["variant"], r["repetition"], r["arm"], r["cycles"]) for r in records]
    if set(identities) != expected or len(identities) != len(expected):
        raise ValueError("Incomplete/duplicate run")
    print("Verified frozen filter and", len(records), "unique probe processes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "run", "verify"))
    parser.add_argument("--name", default="run-001")
    args = parser.parse_args()
    {"freeze": freeze, "run": lambda: run(args.name), "verify": lambda: verify(args.name)}[args.command]()
