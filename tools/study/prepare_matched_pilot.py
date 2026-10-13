"""Freeze metadata-only development selection; inspect no patches or outcomes."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PIN = "11c5f1eea954a42132cfd06bf257766a7963e0fd"
PROJECTS = ("cookiecutter", "luigi", "tornado", "tqdm", "PySnooper")
SEED = "skylla-matched-pilot-v1"
COUNT = 6
CAP = 2
HISTORY = ("experiments/rehearsal/cases.json", "experiments/expansion/screening/cases.json",
           "experiments/trajectory-audit/sample.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def exclusions(root=ROOT):
    excluded = set()
    for relative in HISTORY[:2]:
        manifest = read(root / relative)
        for row in manifest["cases"] + manifest.get("screening_exclusions", []):
            excluded.add("bugsinpy:" + row["id"].lower())
    for row in read(root / HISTORY[2])["cases"]:
        excluded.add("swebench:" + row["instance_id"])
    return sorted(excluded)


def select(rows, excluded):
    used, selected = {}, []
    ranked = sorted(rows, key=lambda r: hashlib.sha256((SEED + "|" + r["id"]).encode()).hexdigest())
    for row in ranked:
        if row["id"] in excluded or used.get(row["project"], 0) >= CAP:
            continue
        selected.append(row)
        used[row["project"]] = used.get(row["project"], 0) + 1
        if len(selected) == COUNT:
            break
    if len(selected) != COUNT:
        raise ValueError("Insufficient eligible cases; do not change selection silently")
    return selected


def freeze(output):
    if output.exists():
        raise ValueError("Output exists; use a new version rather than replacing the cohort")
    benchmark = ROOT / "artifacts/sources/BugsInPy"
    actual = subprocess.run(["git", "-C", str(benchmark), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    if actual != PIN:
        raise ValueError("Benchmark pin mismatch")
    dirty = subprocess.run(["git", "-C", str(benchmark), "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True, check=True).stdout
    if dirty:
        raise ValueError("Benchmark tracked files modified")
    rows, excluded = [], exclusions()
    for project in PROJECTS:
        project_root = benchmark / "projects" / project
        for directory in sorted((project_root / "bugs").iterdir()):
            if not directory.is_dir() or not directory.name.isdigit():
                continue
            info = directory / "bug.info"
            fields = dict(re.findall(r'([a-z_]+)\s*=\s*"([^\"]*)"', info.read_text(encoding="utf-8")))
            rows.append({"id": "bugsinpy:" + project.lower() + "-" + directory.name,
                         "project": project, "bug": int(directory.name),
                         "buggy_commit": fields["buggy_commit_id"], "benchmark_python": fields["python_version"],
                         "benchmark_metadata_sha256": sha(info)})
    selected = select(rows, excluded)
    inventory = {"schema_version": 1, "benchmark_commit": PIN, "eligible_projects": list(PROJECTS),
                 "eligibility_reason": "Small Python library projects from prior local apparatus experience; excludes heavy ML and network-dependent projects. No success filtering.",
                 "selection_seed": SEED, "selection": "Ascending SHA256(seed|id), exclude prior exposure, at most two per project, first six",
                 "scope": "Previously unexamined case IDs in this research, metadata-only development pilot; not confirmation or proof of model-unseen data",
                 "history_sha256": {p: sha(ROOT / p) for p in HISTORY},
                 "excluded_ids": excluded, "eligible_inventory_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
                 "eligible_inventory": rows, "selected": selected,
                 "implementation_sha256": sha(Path(__file__)),
                 "dispositions": [{"id": r["id"], "status": "pending_screening"} for r in selected]}
    arms = ["native", "normalization", "structural_observations", "structural_plus_laya"]
    schedule = []
    for row in selected:
        order = sorted(arms, key=lambda arm: hashlib.sha256((SEED + "|" + row["id"] + "|" + arm).encode()).hexdigest())
        schedule.extend({"case_id": row["id"], "arm": arm, "order_in_case": index} for index, arm in enumerate(order))
    config = {"schema_version": 1, "status": "draft_not_execution_ready", "cohort_sha256": None,
              "coding_backend": None, "coding_model_revision": None, "harness_revision": None,
              "budget": {"total_seconds_per_episode": None, "max_model_tokens_per_episode": None,
                         "max_tool_calls_per_episode": None, "total_inference_spend_cap": None},
              "required_neural_device": "cuda", "cpu_inference_fallback": False,
              "arms": arms, "schedule": schedule,
              "missing_gates": ["coding_backend_and_budget", "per_case_runtime_and_bug_reproduction",
                                "independent_target_and_regression_checks", "source_trace_localization_adapter",
                                "laya_candidate_ranking_contract_and_shadow_validation", "full_process_logging_and_deadline_enforcement"],
              "note": "Schedule is a proposal. Laya action classification is not candidate ranking; the final arm cannot run until its implementation is frozen."}
    output.mkdir(parents=True)
    write(output / "cohort.json", inventory)
    config["cohort_sha256"] = sha(output / "cohort.json")
    write(output / "run-config.draft.json", config)
    print(json.dumps({"selected": [r["id"] for r in selected], "status": config["status"]}))


def verify(output):
    inventory, config = read(output / "cohort.json"), read(output / "run-config.draft.json")
    if config["cohort_sha256"] != sha(output / "cohort.json"):
        raise ValueError("Cohort drift")
    if inventory["implementation_sha256"] != sha(Path(__file__)):
        raise ValueError("Selection implementation drift")
    if inventory["history_sha256"] != {p: sha(ROOT / p) for p in HISTORY} or inventory["excluded_ids"] != exclusions():
        raise ValueError("Exposure inventory drift; create a new cohort version")
    rows = inventory["eligible_inventory"]
    if inventory["eligible_inventory_sha256"] != hashlib.sha256(canonical(rows).encode()).hexdigest():
        raise ValueError("Inventory drift")
    if inventory["selected"] != select(rows, inventory["excluded_ids"]):
        raise ValueError("Selection drift")
    print(json.dumps({"status": "verified_selection_only", "selected_cases": len(inventory["selected"]),
                      "execution_ready": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "verify"))
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/matched-pilot/v1")
    args = parser.parse_args()
    (freeze if args.command == "freeze" else verify)(args.output)
