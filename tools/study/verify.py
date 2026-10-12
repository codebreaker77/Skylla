"""Verify recorded development hashes and summarize observation differences."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/expansion"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_log(record, directory):
    path = (ROOT / record["raw_log"]).resolve()
    require(path.is_relative_to((ROOT / directory).resolve()), "Unexpected raw log location")
    if not path.exists():
        return None
    require(digest(path) == record["raw_log_sha256"], "Changed raw log: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    manifest = json.loads((CONFIG / "screening/cases.json").read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in manifest["cases"]}
    screen = json.loads((CONFIG / "screening/results.json").read_text(encoding="utf-8"))
    require(screen["manifest_sha256"] == digest(CONFIG / "screening/cases.json"), "Changed case manifest")
    screening_logs = 0
    runs = 0
    for attempt in screen["results"]:
        require(attempt["id"] in cases, "Unknown case")
        for record in attempt["runs"]:
            screening_logs += verify_log(record, "artifacts/screening") is not None
            runs += 1
    require(runs == screen["recorded_test_processes"], "Screening count mismatch")
    runtime_logs = 0
    runtime_runs = 0
    workspaces = set()
    differences = {}
    for summary_path in sorted((CONFIG / "runtime/results").glob("*/summary.json")):
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        require(summary["contract_sha256"] == digest(CONFIG / "runtime/probes.json"), "Changed probe contracts")
        require(summary["implementation_sha256"] == digest(ROOT / "tools/study/probe_runtime.py"), "Changed probe implementation")
        require(summary["runner_sha256"] == digest(ROOT / "tools/study/run_runtime_probes.py"), "Changed probe runner")
        records = [json.loads(line) for line in (summary_path.parent / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
        require(len(records) == summary["runs"], "Runtime count mismatch")
        identities = set()
        paired = {}
        for record in records:
            identity = (record["case"], record["probe"], record["variant"])
            require(identity not in identities, "Duplicate runtime identity")
            identities.add(identity)
            require(record["commit"] == cases[record["case"]][record["variant"] + "_commit"], "Wrong source commit")
            require(record["seconds"] >= 0, "Negative duration")
            raw = verify_log(record, "artifacts/runtime-probes")
            if raw is not None:
                require(raw["cwd"] not in workspaces, "Runtime workspace reused")
                workspaces.add(raw["cwd"])
                if record["result"] is not None:
                    require(json.loads(raw["stdout"].splitlines()[-1]) == record["result"], "Observation differs from raw output")
                runtime_logs += 1
            if record["status"] == "observed":
                require(record["result"]["preconditions"]["imported_pinned_source"] is True, "Source-import check failed")
                paired.setdefault((record["case"], record["probe"]), {})[record["variant"]] = record["result"]["observation"]
            runtime_runs += 1
        for (case, probe), variants in paired.items():
            if set(variants) == {"buggy", "fixed"}:
                differences.setdefault(case, []).append(variants["buggy"] != variants["fixed"])
    require(runtime_runs > 0, "No runtime observations")
    print(json.dumps({"screening_records": runs, "available_screening_logs_verified": screening_logs,
                      "runtime_records": runtime_runs, "available_runtime_logs_verified": runtime_logs,
                      "unequal_payload_pairs": {case: {"changed": sum(values), "pairs": len(values)}
                                                for case, values in differences.items()}}, indent=2))
