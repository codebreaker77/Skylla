"""Freeze and replay source-proposed observations on exposed development cases."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from observer_candidates import propose
from process_record import execute, readiness

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/observer-discovery"
sys.path.insert(0, str(ROOT / "tools/pilot"))
from prepare import prepare
from run import fingerprint

FILES = ("tornado/ioloop.py", "tornado/platform/asyncio.py")
IMPLEMENTATIONS = ("tools/study/observer_candidates.py", "tools/study/observer_probe.py",
                   "tools/study/observer_study.py", "tools/study/process_record.py",
                   "tools/pilot/prepare.py", "tools/pilot/run.py")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(data, indent=2, ensure_ascii=True) + "\n")


def cases():
    manifest = json.loads((ROOT / "experiments/expansion/screening/cases.json").read_text(encoding="utf-8"))
    return [c for c in manifest["cases"] if c["id"] in ("tornado-6", "luigi-7")]


def source(case, variant):
    metadata = prepare(case, variant, exclude_symlink_prefixes=("maint/test/appengine/",)
                       if case["id"] == "tornado-6" else ())
    return ROOT / metadata["path"], metadata


def freeze():
    if (CONFIG / "protocol.json").exists() or (CONFIG / "proposals.json").exists():
        raise ValueError("Protocol/proposals already frozen")
    identities = {}
    generated = None
    started = time.perf_counter()
    for case in cases():
        path, metadata = source(case, "buggy")
        identities[case["id"]] = {"commit": metadata["commit"], "source_sha256": fingerprint(path)}
        if case["id"] == "tornado-6":
            generated = propose(path, FILES)
    write(CONFIG / "proposals.json", {"schema_version": 1, "case": "tornado-6",
                                     "generated_from": "buggy source only", "source_files": list(FILES),
                                     "candidates": generated})
    write(CONFIG / "protocol.json", {"schema_version": 1, "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                                     "scope": "Exposed development; not a repair or model comparison",
                                     "source_identities": identities, "cases": cases(), "repetitions": 3,
                                     "cycles": [1, 10], "arms": ["normalize", "source_containers"],
                                     "neighbor_tests": {"tornado-6": "tornado.test.asyncio_test.AsyncIOLoopTest.test_asyncio_callback",
                                                        "luigi-7": "test/scheduler_api_test.py::SchedulerApiTest::test_dep"},
                                     "implementation_sha256": {p: sha(ROOT / p) for p in IMPLEMENTATIONS},
                                     "method_sha256": sha(CONFIG / "METHODOLOGY.md"),
                                     "proposals_sha256": sha(CONFIG / "proposals.json"),
                                     "generation_and_source_check_seconds": time.perf_counter() - started})
    print("Frozen", len(generated), "AST proposals before paired execution")


def validate_protocol():
    protocol = json.loads((CONFIG / "protocol.json").read_text(encoding="utf-8"))
    for relative, digest in protocol["implementation_sha256"].items():
        if sha(ROOT / relative) != digest:
            raise ValueError("Changed frozen implementation: " + relative)
    if sha(CONFIG / "METHODOLOGY.md") != protocol["method_sha256"] or sha(CONFIG / "proposals.json") != protocol["proposals_sha256"]:
        raise ValueError("Changed frozen method/proposals")
    return protocol


def workspace(source_path, case):
    directory = ROOT / "workspaces/observer-discovery"
    directory.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=case["id"] + "-", dir=directory))
    shutil.copytree(source_path, work, dirs_exist_ok=True)
    runtime = work / ".runtime"
    runtime.mkdir()
    env = {k: os.environ[k] for k in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC") if k in os.environ}
    env.update(PYTHONPATH=str(work), PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
               PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
               TEMP=str(runtime), TMP=str(runtime), HOME=str(runtime), USERPROFILE=str(runtime))
    return work, env


def run(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("Unsafe run name")
    protocol = validate_protocol()
    output = CONFIG / "results" / name
    output.mkdir(parents=True, exist_ok=False)
    records = []

    def record(case, variant, kind, work, env, argv, **extra):
        observation = execute(argv, work, env, timeout=30)
        observation.update(case=case["id"], variant=variant, kind=kind, **extra)
        records.append(observation)
        write(output / "processes.json", records)
        print(case["id"], variant, kind, observation["returncode"], flush=True)
        return observation

    started = time.perf_counter()
    dispositions = []
    for case in protocol["cases"]:
        for variant in ("buggy", "fixed"):
            path, metadata = source(case, variant)
            identity = fingerprint(path)
            if variant == "buggy" and identity != protocol["source_identities"][case["id"]]["source_sha256"]:
                raise ValueError("Changed source used for proposal generation")
            work, env = workspace(path, case)
            prefix = [sys.executable, str(ROOT / "tools/study/observer_probe.py"), "--case", case["id"]]
            check = record(case, variant, "readiness", work, env, prefix + ["--readiness"],
                           source_sha256=identity, commit=metadata["commit"])
            if not readiness(check, case["id"]):
                dispositions.append({"case": case["id"], "variant": variant, "status": "blocked_readiness"})
                continue
            dispositions.append({"case": case["id"], "variant": variant, "status": "ready"})
            for repetition in range(protocol["repetitions"]):
                arms = protocol["arms"] if case["id"] == "tornado-6" else ["normalize"]
                cycles = protocol["cycles"] if case["id"] == "tornado-6" else [1]
                for arm in arms:
                    for count in cycles:
                        work, env = workspace(path, case)
                        argv = prefix + ["--arm", arm, "--cycles", str(count)]
                        if arm == "source_containers":
                            argv += ["--candidates", str(CONFIG / "proposals.json")]
                        record(case, variant, "probe", work, env, argv, arm=arm, cycles=count,
                               repetition=repetition, source_sha256=identity, commit=metadata["commit"])
            # Evaluator-only reference regression fixtures, never used by AST proposals.
            fixed_path, _ = source(case, "fixed")
            for target in case["targets"] + [protocol["neighbor_tests"][case["id"]]]:
                work, env = workspace(path, case)
                shutil.copyfile(fixed_path / case["test_file"], work / case["test_file"])
                argv = [sys.executable, "-m", "unittest", "-q", target] if case["test_mode"] == "unittest" else [
                    sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target]
                record(case, variant, "reference_test", work, env, argv, target=target,
                       source_sha256=identity, fixture_sha256=sha(fixed_path / case["test_file"]), commit=metadata["commit"])
    write(output / "summary.json", {"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
                                   "scope": protocol["scope"], "python": sys.version,
                                   "packages": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
                                   "dispositions": dispositions, "processes": len(records),
                                   "protocol_sha256": sha(CONFIG / "protocol.json"),
                                   "processes_sha256": sha(output / "processes.json"),
                                   "process_elapsed_seconds": sum(r["elapsed_seconds"] for r in records),
                                   "runner_elapsed_seconds": time.perf_counter() - started})


def verify(name):
    validate_protocol()
    output = CONFIG / "results" / name
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    if summary["protocol_sha256"] != sha(CONFIG / "protocol.json") or summary["processes_sha256"] != sha(output / "processes.json"):
        raise ValueError("Artifact hash mismatch")
    records = json.loads((output / "processes.json").read_text(encoding="utf-8"))
    if len(records) != summary["processes"]:
        raise ValueError("Process count mismatch")
    print("Verified frozen proposal/implementation and recorded process integrity:", len(records), "processes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "run", "verify"))
    parser.add_argument("--name", default="run-001")
    args = parser.parse_args()
    {"freeze": freeze, "run": lambda: run(args.name), "verify": lambda: verify(args.name)}[args.command]()
