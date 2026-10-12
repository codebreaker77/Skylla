"""Preserve every screening attempt and review triage without rewriting raw results."""

import hashlib
import json
from pathlib import Path
from screen import classify

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/expansion/screening"


if __name__ == "__main__":
    manifest = json.loads((CONFIG / "cases.json").read_text(encoding="utf-8"))
    known = {case["id"]: case for case in manifest["cases"]}
    attempts = []
    for summary_path in sorted((ROOT / "artifacts/screening").glob("*/summary.json")):
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        for case in summary["cases"]:
            review = dict(case)
            review["attempt"] = summary_path.parent.name
            review["timestamp_utc"] = summary["timestamp_utc"]
            review["python"] = summary["python"]
            review["packages"] = summary.get("packages")
            review["runner_sha256"] = summary.get("runner_sha256")
            review["environment_policy"] = summary.get("environment_policy")
            review["benchmark_commit"] = summary.get("benchmark_commit")
            review["manifest_sha256"] = summary.get("manifest_sha256")
            review["original_admitted"] = case.get("admitted", False)
            review["repeats_required"] = summary["repeats"]
            runs = []
            for record in case.get("runs", []):
                log = ROOT / record["raw_log"]
                if hashlib.sha256(log.read_bytes()).hexdigest() != record["raw_log_sha256"]:
                    raise ValueError("Changed raw log: " + str(log))
                raw = json.loads(log.read_text(encoding="utf-8"))
                status = record["status"] if record["status"] == "timeout" else classify(
                    known[case["id"]]["test_mode"], record["exit_code"], raw["stdout"] + raw["stderr"])
                runs.append(dict(record, original_status=record["status"], reviewed_status=status))
            review["runs"] = runs
            states = {v: [run["reviewed_status"] for run in runs if run["variant"] == v]
                      for v in ("buggy", "fixed")}
            n = summary["repeats"]
            review["reviewed_admitted"] = states == {"buggy": ["failed"] * n, "fixed": ["passed"] * n} and n == 3
            attempts.append(review)
    selected = {}
    for attempt in sorted(attempts, key=lambda value: value["timestamp_utc"]):
        selected[attempt["id"]] = attempt
    payload = {"schema_version": 1, "purpose": "Development screening; not repair success or a frozen holdout",
               "triage_review": "Fixture/loader/skipped-test handling corrected after inspecting setup failures; original statuses retained",
               "manifest_sha256": hashlib.sha256((CONFIG / "cases.json").read_bytes()).hexdigest(),
               "candidates": len(known), "attempts": len(attempts),
               "recorded_test_processes": sum(len(attempt["runs"]) for attempt in attempts),
               "latest_admitted_ids": sorted(key for key, value in selected.items() if value["reviewed_admitted"]),
               "latest_not_admitted_ids": sorted(key for key, value in selected.items() if not value["reviewed_admitted"]),
               "results": attempts}
    (CONFIG / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "results"}, indent=2))
