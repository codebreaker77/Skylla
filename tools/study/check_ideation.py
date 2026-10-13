"""Reproduce design counterexamples; these are not agent or repair benchmarks."""

import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from skylla import decide


def hypothesis_duplication():
    request = {
        "schema_version": 1, "state_id": "unchanged-state",
        "hypotheses": ["A", "B", "C"], "required_controls": [],
        "budget": {"remaining_seconds": 10, "remaining_expansions": 0,
                   "expansion_estimated_seconds": 1}, "candidates": [],
    }
    for name, cost, predictions in (
        ("probe-a", 1, {"A": "yes", "B": "no", "C": "no"}),
        ("probe-c", 1.25, {"A": "no", "B": "no", "C": "yes"}),
    ):
        request["candidates"].append({
            "id": name, "state_id": "unchanged-state", "argv": ["python", name + ".py"],
            "outcomes": ["yes", "no"], "predictions": predictions,
            "estimated_seconds": cost,
            "preconditions": [{"id": "source", "state_id": "unchanged-state", "status": "passed"}],
        })
    reworded = copy.deepcopy(request)
    reworded["hypotheses"].append("C_reworded")
    for candidate in reworded["candidates"]:
        candidate["predictions"]["C_reworded"] = candidate["predictions"]["C"]
    before, after = decide(request), decide(reworded)
    # The experiment author declares C_reworded an alias of C. The current
    # schema does not encode that relation; predictions alone cannot establish it.
    return {
        "kind": "constructed counterexample against current controller",
        "alias_assumption": "C_reworded denotes the same explanation as C",
        "before": {"selected": before["candidate_id"], "counts": before["contrast_counts"]},
        "after": {"selected": after["candidate_id"], "counts": after["contrast_counts"]},
        "choice_changed": before["candidate_id"] != after["candidate_id"],
        "limitation": "Does not imply hypotheses with matching predictions are semantically equivalent",
    }


def observation_projection():
    source = ROOT / "experiments/expansion/runtime/results/run-001/observations.jsonl"
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    pairs = {}
    for record in records:
        if record["case"] == "tornado-6" and record["status"] == "observed":
            pairs.setdefault(record["probe"], {})[record["variant"]] = record["result"]["observation"]
    rows = []
    for probe, variants in sorted(pairs.items()):
        if set(variants) != {"buggy", "fixed"}:
            raise ValueError("Unpaired observation: " + probe)
        rows.append({"probe": probe,
                     "native_closed": {v: obs["all_native_loops_closed"] for v, obs in variants.items()},
                     "registry_delta": {v: obs["mapping_delta_after"] for v, obs in variants.items()}})
    # Hash parsed data canonically so Windows CRLF and Git LF copies agree.
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"kind": "post-hoc projection of existing observations; no new target executions",
            "source": source.relative_to(ROOT).as_posix(),
            "parsed_records_sha256": hashlib.sha256(canonical).hexdigest(),
            "pairs": rows,
            "changed_native_closed_pairs": sum(row["native_closed"]["buggy"] != row["native_closed"]["fixed"] for row in rows),
            "changed_registry_pairs": sum(row["registry_delta"]["buggy"] != row["registry_delta"]["fixed"] for row in rows),
            "limitation": "Observer field chosen after seeing results; no automatic discovery or held-out result"}


def null_result_ambiguity():
    # A deliberately simplified deterministic model. H is a real contrast,
    # R means the intervention reaches it, O means the observer transmits it.
    worlds = [{"H": h, "R": r, "O": o, "Y": h * r * o}
              for h, r, o in itertools.product((0, 1), repeat=3)]
    null_worlds = [world for world in worlds if world["Y"] == 0]
    adequate_null = [world for world in null_worlds if world["R"] == world["O"] == 1]
    require(len(null_worlds) == 7, "Unexpected truth table")
    require({world["H"] for world in null_worlds} == {0, 1}, "Null result unexpectedly identifies H")
    require(len(adequate_null) == 1 and adequate_null[0]["H"] == 0, "Invalid model deduction")
    return {"kind": "exhaustive truth table for an assumed Boolean model",
            "equation": "Y = H * R * O", "worlds": worlds,
            "null_worlds": len(null_worlds), "H_values_compatible_with_null": [0, 1],
            "limitation": "R and O are latent model variables, not implemented oracles; noise and confounding omitted"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the design-check record")
    args = parser.parse_args()
    result = {"schema_version": 1,
              "purpose": "Design falsification; no novelty, prevalence, or repair-performance claim",
              "controller_sha256": hashlib.sha256((ROOT / "src/skylla/decision.py").read_bytes()).hexdigest(),
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "hypothesis_duplication": hypothesis_duplication(),
              "observation_projection": observation_projection(),
              "null_result_ambiguity": null_result_ambiguity()}
    output = ROOT / "experiments/ideation/design-checks.json"
    if args.write:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads(output.read_text(encoding="utf-8")), "Design-check record differs; investigate before updating")
    print(json.dumps({"hypothesis_alias_changes_choice": result["hypothesis_duplication"]["choice_changed"],
                      "tornado_native_closed_differences": result["observation_projection"]["changed_native_closed_pairs"],
                      "tornado_registry_differences": result["observation_projection"]["changed_registry_pairs"],
                      "null_result_compatible_worlds": result["null_result_ambiguity"]["null_worlds"]}, indent=2))
