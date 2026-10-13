"""Post-run contract checks, descriptive timings and stability; not accuracy."""

import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "experiments/judge-baseline/results/laya-gpu-001"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path = RUN / "analysis.json"
    if path.exists():
        raise ValueError("Analysis exists; preserve original")
    records = json.loads((RUN / "decisions.json").read_text(encoding="utf-8"))
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    valid = [r for r in records if r["status"] == "completed"]
    violations = [r for r in valid if r["recommendation"]["action"] == "repair_setup"
                  and "failed" not in r["state"]["evidence"]["preconditions"]]
    times = [r["recommendation"]["inference_seconds"] for r in valid]
    groups = []
    for state_id in sorted({r["state"]["state_id"] for r in records}):
        group = [r for r in valid if r["state"]["state_id"] == state_id]
        first = group[0] if group else None
        answer = first["recommendation"]["provider_calls"][0]["answers"]["choices"]["label"] if first else None
        groups.append({"state_id": state_id, "completed": len(group),
                       "actions": sorted({r["recommendation"]["action"] or "NONE" for r in group}),
                       "median_inference_seconds": statistics.median(r["recommendation"]["inference_seconds"] for r in group) if group else None,
                       "original_first_answer": answer,
                       "setup_repair_without_failed_precondition": sum(r in violations for r in group)})
    probability_changes = []
    for comparison in summary["order_comparisons"]:
        pair = [r for r in valid if r["state"]["state_id"] == comparison["state_id"] and r["repetition"] == comparison["repetition"]]
        if len(pair) != 2:
            continue
        distributions = [r["recommendation"]["provider_calls"][0]["answers"]["choices"]["label"]["probabilities"] for r in pair]
        probability_changes.append({"state_id": comparison["state_id"], "repetition": comparison["repetition"],
                                    "total_variation": sum(abs(distributions[0][k]-distributions[1][k]) for k in distributions[0])/2})
    value = {"schema_version": 1, "analysis_type": "post-run descriptive and declared-action contract review",
             "source_sha256": {p: sha(RUN / p) for p in ("decisions.json", "summary.json", "warmup.json", "protocol.json")},
             "script_sha256": sha(Path(__file__)), "groups": groups,
             "completed_decisions": len(valid), "declared_setup_contract_violations": len(violations),
             "median_inference_seconds": statistics.median(times) if times else None,
             "min_inference_seconds": min(times) if times else None, "max_inference_seconds": max(times) if times else None,
             "probability_order_changes": probability_changes,
             "loader_warning": {"source": "RuntimeWarning captured by execution tool; checkpoint config independently inspected",
                                "bucket": "choice:11+", "stored_temperature": 0.10058280825614929,
                                "runtime_clipped_temperature": 0.5,
                                "current_options": 6, "current_bucket": "choice:6-10",
                                "debugging_calibration": "not established"},
             "scope": "Three exposed states across two bugs, repeated twelve times; no independent correct-action or repair labels"}
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
    print(json.dumps({"completed": len(valid), "unsupported_setup_repair": len(violations),
                      "median_ms": value["median_inference_seconds"]*1000, "groups": groups}, indent=2))


if __name__ == "__main__":
    main()
