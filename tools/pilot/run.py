"""Run the local rehearsal; never invokes models or harness credentials."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/rehearsal"


def fingerprint(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def execute(case, variant, name, output, test=False, targets=None):
    source = ROOT / "artifacts/sources" / (case["id"] + "-" + variant)
    metadata = json.loads((source / ".skylla-source.json").read_text(encoding="utf-8"))
    if metadata["commit"] != case[variant + "_commit"]:
        raise ValueError("Source snapshot commit mismatch")
    workspace_root = ROOT / "workspaces/rehearsal"
    workspace_root.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=case["id"] + "-", dir=workspace_root))
    shutil.copytree(source, work, dirs_exist_ok=True)
    if test:
        # Match the benchmark's fixed regression fixture on both source variants.
        fixture = ROOT / "artifacts/sources" / (case["id"] + "-fixed") / case["test_file"]
        shutil.copyfile(fixture, work / case["test_file"])
        argv = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
        argv.extend(targets or [case["test_target"]])
    else:
        shutil.copyfile(ROOT / "tools/pilot/probe.py", work / "probe.py")
        argv = [sys.executable, "probe.py", "--case", case["id"], "--probe", name]
    before = fingerprint(work)
    scratch = work / "runtime"
    scratch.mkdir()
    env = {key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "PATH", "COMSPEC")
           if key in os.environ}
    env.update({"TEMP": str(scratch), "TMP": str(scratch), "HOME": str(scratch),
                "USERPROFILE": str(scratch), "PYTHONPATH": str(work),
                "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0",
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    started = time.perf_counter()
    try:
        result = subprocess.run(argv, cwd=work, env=env, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=30)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
        status = ("passed" if code == 0 else
                  "failed" if test and code == 1 else "setup_failure")
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else (value or "")
        stdout, stderr, code = decode(error.stdout), decode(error.stderr), None
        status = "timeout"
    elapsed = time.perf_counter() - started
    log_root = ROOT / "artifacts/rehearsal" / output.name
    log_root.mkdir(parents=True, exist_ok=True)
    log = log_root / (case["id"] + "-" + variant + "-" + name + ".json")
    log.write_text(json.dumps({"argv": argv, "cwd": str(work), "stdout": stdout,
                               "stderr": stderr}, indent=2) + "\n", encoding="utf-8")
    record = {"case": case["id"], "variant": variant, "run": name,
              "commit": metadata["commit"], "archive_sha256": metadata["archive_sha256"],
              "starting_state_sha256": before, "exit_code": code, "status": status,
              "seconds": round(elapsed, 6), "raw_log": log.relative_to(ROOT).as_posix(),
              "raw_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
    if not test:
        try:
            record["observation"] = json.loads(stdout.splitlines()[-1])
            record["status"] = "setup_failure" if "setup_failure" in record["observation"] else "observed"
        except (ValueError, IndexError):
            if status != "timeout":
                record["status"] = "unexpected"
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--regressions-only", action="store_true")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(CONFIG.resolve()):
        parser.error("Output must be inside experiments/rehearsal")
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((CONFIG / "cases.json").read_text(encoding="utf-8"))
    probe_bytes = (CONFIG / "probes.json").read_bytes()
    probes = json.loads(probe_bytes)
    regressions = json.loads((CONFIG / "regressions.json").read_text(encoding="utf-8"))
    records = []
    with (output / "observations.jsonl").open("w", encoding="utf-8") as stream:
        for case in manifest["cases"]:
            for variant in ("buggy", "fixed"):
                if args.regressions_only:
                    record = execute(case, variant, "regressions", output, test=True,
                                     targets=regressions[case["id"]])
                    records.append(record)
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                    print(case["id"], variant, "regressions", record["status"], flush=True)
                    continue
                for repeat in range(3):
                    record = execute(case, variant, "baseline-" + str(repeat + 1), output, test=True)
                    records.append(record)
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                    print(case["id"], variant, record["run"], record["status"], flush=True)
                for probe in probes["cases"][case["id"]]["probes"]:
                    record = execute(case, variant, probe["id"], output)
                    records.append(record)
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                    print(case["id"], variant, record["run"], record["status"], flush=True)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True,
                            text=True, check=True).stdout.splitlines()
    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Development execution feasibility; no agent repair comparison",
        "python": sys.version, "platform": platform.platform(), "packages": freeze,
        "cases_sha256": hashlib.sha256((CONFIG / "cases.json").read_bytes()).hexdigest(),
        "probe_contracts_sha256": hashlib.sha256(probe_bytes).hexdigest(),
        "probe_implementation_sha256": hashlib.sha256((ROOT / "tools/pilot/probe.py").read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "regressions_only": args.regressions_only,
        "regression_targets_sha256": hashlib.sha256((CONFIG / "regressions.json").read_bytes()).hexdigest(),
        "total_execution_seconds": round(sum(r["seconds"] for r in records), 6),
        "runs": len(records), "cases": [],
    }
    for case in manifest["cases"]:
        selected = [r for r in records if r["case"] == case["id"]]
        if args.regressions_only:
            summary["cases"].append({"id": case["id"], "regressions":
                                     {r["variant"]: r["status"] for r in selected}})
            continue
        baselines = {variant: [r["status"] for r in selected if r["variant"] == variant
                               and r["run"].startswith("baseline-")]
                     for variant in ("buggy", "fixed")}
        summary["cases"].append({"id": case["id"], "baselines": baselines,
                                 "admitted": baselines == {"buggy": ["failed"] * 3, "fixed": ["passed"] * 3}})
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
