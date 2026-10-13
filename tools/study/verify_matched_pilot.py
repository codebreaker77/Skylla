"""Check recorded selection, process artifacts and versioned native protocols."""

import hashlib
import json
from pathlib import Path
import subprocess

from prepare_matched_pilot import ROOT, sha, read, verify
from action_admissibility import check


def require(condition, message):
    if not condition:
        raise ValueError(message)


def versioned_hash(relative, expected, revisions):
    if sha(ROOT / relative) == expected:
        return
    for revision in revisions:
        result = subprocess.run(["git", "show", revision + ":" + relative], capture_output=True)
        if result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == expected:
            return
    raise ValueError("Missing recorded implementation: " + relative)


def main():
    verify(ROOT / "experiments/matched-pilot/v1")
    folder = ROOT / "experiments/matched-pilot"
    replay = read(folder / "admissibility-replay.json")
    source = ROOT / "experiments/judge-baseline/results/laya-gpu-001/decisions.json"
    require(replay["source_sha256"] == sha(source), "Shadow source drift")
    require(replay["implementation_sha256"] == sha(ROOT / "tools/study/action_admissibility.py"), "Contract implementation drift")
    predictions = read(source)
    require(len(predictions) == len(replay["records"]), "Missing replay predictions")
    for record, row in zip(predictions, replay["records"]):
        decision = check(record["state"], record["recommendation"]["action"])
        require(all(row[k] == v for k, v in decision.items()), "Contract replay drift")
    screen = folder / "screening/run-001"
    summary, protocol = read(screen / "summary.json"), read(screen / "protocol.json")
    require(summary["protocol_sha256"] == sha(screen / "protocol.json"), "Screen protocol drift")
    require(protocol["method_sha256"] == sha(folder / "METHODOLOGY.md"), "Frozen screen method drift")
    require(protocol["cohort_sha256"] == sha(folder / "v1/cohort.json"), "Screen cohort drift")
    for relative, expected in protocol["implementation_sha256"].items():
        require(sha(ROOT / relative) == expected, "Screen implementation drift")
    selected = {r["id"] for r in read(folder / "v1/cohort.json")["selected"]}
    require({r["case_id"] for r in summary["cases"]} == selected, "Screen cases drift")
    for case in summary["cases"]:
        for record in case["runs"]:
            if "log" in record:
                require(sha(ROOT / record["log"]) == record["log_sha256"], "Screen process drift")
    review = read(folder / "screening/review-001.json")
    for filename, expected in review["sources_sha256"].items():
        require(sha(screen / filename) == expected, "Screen review source drift")
    runtime = read(folder / "sandbox-runtime-check.json")
    require(runtime["implementation_sha256"] == sha(ROOT / "tools/study/check_sandbox_runtime.py"), "Runtime check implementation drift")
    historical_manifest = ROOT / "artifacts/harness-smoke/runtime-manifest-check.json"
    if historical_manifest.exists():
        require(sha(historical_manifest) == runtime["runtime_manifest_sha256"], "Historical runtime manifest drift")
    absent = []
    for native in sorted((folder / "native-feasibility").glob("run-*")):
        protocol, summary = read(native / "protocol.json"), read(native / "summary.json")
        require(summary["protocol_sha256"] == sha(native / "protocol.json"), "Native protocol drift")
        revision = protocol.get("launcher_revision", 1)
        method = "NATIVE_FEASIBILITY.md" if revision == 1 else "NATIVE_FEASIBILITY_V%d.md" % revision
        require(sha(folder / method) == protocol["method_sha256"], "Native method drift")
        versioned_hash("tools/study/run_native_feasibility.py", protocol["script_sha256"], ["015121d", "07a7aae"])
        for case in summary["cases"]:
            name = case["case_id"].split(":", 1)[1]
            require(read(native / (name + "-summary.json")) == case, "Native case summary drift")
            for evaluation in case["evaluation"]:
                require(sha(native / (name + "-" + evaluation["kind"] + ".json")) == evaluation["record_sha256"], "Evaluation drift")
            private = ROOT / "artifacts/matched-native" / native.name
            for suffix, expected in ((".stdout.jsonl", case["inference"]["stdout_sha256"]),
                                     (".stderr.txt", case["inference"]["stderr_sha256"]),
                                     (".patch", case["patch_sha256"])):
                path = private / (name + suffix)
                if path.exists():
                    require(sha(path) == expected, "Private native artifact drift")
                else:
                    absent.append(path.relative_to(ROOT).as_posix())
    print(json.dumps({"status": "recorded_artifact_hashes_verified", "screened_cases": len(selected),
                      "private_native_files_unavailable": absent,
                      "scope": "Artifact verification, not statistical validation or a comparison result"}))


if __name__ == "__main__":
    main()
