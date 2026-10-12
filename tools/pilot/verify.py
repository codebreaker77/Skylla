"""Check recorded manifests, raw-log hashes when present, and independent run directories."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/rehearsal"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    cases = json.loads((CONFIG / "cases.json").read_text(encoding="utf-8"))
    by_id = {case["id"]: case for case in cases["cases"]}
    verified = 0
    local_logs = 0
    workspaces = set()
    for summary_path in sorted((CONFIG / "results").glob("*/summary.json")):
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        require(summary["cases_sha256"] == digest(CONFIG / "cases.json"), "Case manifest changed")
        require(summary["probe_contracts_sha256"] == digest(CONFIG / "probes.json"), "Probe contracts changed")
        require(summary["probe_implementation_sha256"] == digest(ROOT / "tools/pilot/probe.py"), "Probe implementation changed")
        records = [json.loads(line) for line in
                   (summary_path.parent / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
        require(len(records) == summary["runs"], "Run count mismatch")
        identities = set()
        for record in records:
            identity = (record["case"], record["variant"], record["run"])
            require(identity not in identities, "Duplicate run identity")
            identities.add(identity)
            case = by_id[record["case"]]
            require(record["commit"] == case[record["variant"] + "_commit"], "Wrong source commit")
            require(record["status"] in ("passed", "failed", "observed", "setup_failure", "timeout", "unexpected"), "Unknown status")
            require(record["seconds"] >= 0, "Negative duration")
            log = (ROOT / record["raw_log"]).resolve()
            require(log.is_relative_to((ROOT / "artifacts/rehearsal").resolve()), "Unexpected log location")
            if log.exists():
                require(digest(log) == record["raw_log_sha256"], "Raw log changed")
                data = json.loads(log.read_text(encoding="utf-8"))
                require(data["cwd"] not in workspaces, "Workspace reused across independent runs")
                workspaces.add(data["cwd"])
                if "observation" in record:
                    require(json.loads(data["stdout"].splitlines()[-1]) == record["observation"], "Observation differs from raw output")
                local_logs += 1
            verified += 1
    require(verified > 0, "No recorded runs found")
    print("Verified", verified, "records;", local_logs, "local raw logs checked")
