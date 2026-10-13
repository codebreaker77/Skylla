"""Post-run paired analysis of the frozen controlled probe-repair study."""

import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/probe-repair"
RUN = STUDY / "results/run-001"


def paired_key(record):
    return tuple(record["request"][key] for key in ("family", "condition", "fault_present", "seed"))


if __name__ == "__main__":
    source = RUN / "episodes.jsonl"
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    protocol = json.loads((STUDY / "protocol.json").read_text(encoding="utf-8"))
    if hashlib.sha256(source.read_bytes()).hexdigest() != summary["episodes_sha256"]:
        raise ValueError("Episode record hash changed")
    grouped = {}
    for record in records:
        grouped.setdefault(paired_key(record), {})[record["request"]["arm"]] = record
    for key, group in grouped.items():
        if set(group) != set(protocol["arms"]):
            raise ValueError("Incomplete matched cell: " + str(key))
        public = [record["episode"]["public_input"] for record in group.values() if record["episode"]]
        if any(value != public[0] for value in public):
            raise ValueError("Arms did not receive identical public menus")
    comparisons = {}
    for other in protocol["arms"]:
        if other == "conditional_calibrate":
            continue
        wins, losses, ties, differences = 0, 0, 0, []
        for key, group in grouped.items():
            candidate = group["conditional_calibrate"]["episode"]
            baseline = group[other]["episode"]
            if key[2]:
                a = bool(candidate and candidate["verified_discriminator"])
                b = bool(baseline and baseline["verified_discriminator"])
                wins += a and not b
                losses += b and not a
                ties += a == b
            if candidate is not None and baseline is not None:
                differences.append(candidate["invocations"] - baseline["invocations"])
        comparisons[other] = {"positive_wins": wins, "positive_losses": losses, "positive_ties": ties,
                              "completed_cost_pairs": len(differences),
                              "mean_extra_invocations_conditional": statistics.mean(differences)}
    by_seed = {}
    for arm in protocol["arms"]:
        by_seed[arm] = {}
        for seed in protocol["seeds"]:
            subset = [record for record in records if record["request"]["arm"] == arm
                      and record["request"]["seed"] == seed and record["request"]["fault_present"]]
            by_seed[arm][str(seed)] = {"positive_episodes": len(subset),
                "verified": sum(bool(record["episode"] and record["episode"]["verified_discriminator"]) for record in subset)}
    example = next(record for record in records if record["request"] == {
        "family": "configuration", "condition": "source_and_observer", "fault_present": True,
        "seed": 101, "arm": "conditional_calibrate", "budget": 8})
    trace = [{"invocation": entry["invocation"], "kind": entry["kind"], "probe": entry["probe"],
              "receipt": entry["receipt"]} for entry in example["episode"]["trace"]]
    result = {"schema_version": 1, "analysis_status": "Post-run descriptive analysis; no new target executions",
              "episodes_sha256": summary["episodes_sha256"],
              "analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "paired_conditional_vs": comparisons, "positive_results_by_order_seed": by_seed,
              "total_policy_invocations": sum(row["target_invocations"] for row in summary["arms"].values()),
              "total_reference_invocations": sum(row["reference_invocations"] for row in summary["arms"].values()),
              "example_episode_id": example["id"], "example_trace": trace}
    with (RUN / "analysis.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("example_trace", "positive_results_by_order_seed")}, indent=2))
