"""Post-run descriptive comparisons; never label an action's repair utility."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments/observer-discovery"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(name):
    output = CONFIG / "results" / name
    records_path = output / "processes.json"
    records = json.loads(records_path.read_text(encoding="utf-8"))
    protocol = json.loads((CONFIG / "protocol.json").read_text(encoding="utf-8"))
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    if summary["processes_sha256"] != sha(records_path):
        raise ValueError("Process records changed")
    grouped = {}
    failures = []
    for record in records:
        if record["kind"] != "probe":
            continue
        key = (record["case"], record["arm"], record["cycles"], record["repetition"])
        variants = grouped.setdefault(key, {})
        if record["variant"] in variants:
            raise ValueError("Duplicate probe identity")
        payload = record["payload"]
        valid = (record["returncode"] == 0 and isinstance(payload, dict)
                 and payload.get("case") == record["case"] and payload.get("imported_pinned_source") is True)
        if not valid:
            failures.append({"identity": list(key), "variant": record["variant"]})
        variants[record["variant"]] = payload.get("observation") if valid else None
    pairs = []
    candidate_pairs = {}
    for key, variants in sorted(grouped.items()):
        buggy, fixed = variants.get("buggy"), variants.get("fixed")
        comparable = buggy is not None and fixed is not None
        pairs.append({"case": key[0], "arm": key[1], "cycles": key[2], "repetition": key[3],
                      "comparable": comparable, "different": buggy != fixed if comparable else None})
        if not comparable or key[1] != "source_containers":
            continue
        candidates = json.loads((CONFIG / "proposals.json").read_text(encoding="utf-8"))["candidates"]
        for candidate in candidates:
            cid = candidate["id"]
            def vector(observation):
                # Only compare accesses valid on both versions. Unavailable is
                # not a zero length or a negative bug result.
                readings = []
                if candidate["scope"] == "class":
                    readings.append(observation["before"].get(cid))
                for event in observation["events"]:
                    readings.extend((event["active"].get(cid), event["closed"].get(cid)))
                if candidate["scope"] == "class":
                    readings.append(observation["after"].get(cid))
                valid = all(isinstance(r, dict) and r.get("status") == "observed" for r in readings)
                return [r["length"] for r in readings] if valid else None
            left, right = vector(buggy), vector(fixed)
            result = candidate_pairs.setdefault(cid, {"candidate": candidate, "comparable_pairs": 0,
                                                      "different_pairs": 0, "unavailable_pairs": 0})
            if left is None or right is None:
                result["unavailable_pairs"] += 1
            else:
                result["comparable_pairs"] += 1
                result["different_pairs"] += int(left != right)
    contrasts = []
    for case, arm in sorted({(p["case"], p["arm"]) for p in pairs}):
        group = [p for p in pairs if p["case"] == case and p["arm"] == arm]
        contrasts.append({"case": case, "arm": arm, "pairs": len(group),
                          "comparable_pairs": sum(p["comparable"] for p in group),
                          "different_pairs": sum(p["different"] is True for p in group)})
    expected = {(case["id"], arm, cycles, repetition)
                for case in protocol["cases"]
                for arm in (protocol["arms"] if case["id"] == "tornado-6" else ["normalize"])
                for cycles in (protocol["cycles"] if case["id"] == "tornado-6" else [1])
                for repetition in range(protocol["repetitions"])}
    costs = []
    for case, kind, arm in sorted({(r["case"], r["kind"], r.get("arm", "")) for r in records}):
        group = [r for r in records if (r["case"], r["kind"], r.get("arm", "")) == (case, kind, arm)]
        costs.append({"case": case, "kind": kind, "arm": arm, "processes": len(group),
                      "elapsed_seconds": sum(r["elapsed_seconds"] for r in group)})
    result = {"schema_version": 1, "analysis_type": "post-run descriptive reference contrast",
              "processes_sha256": sha(records_path), "summary_sha256": sha(output / "summary.json"),
              "script_sha256": sha(Path(__file__)), "expected_probe_pairs": len(expected),
              "missing_probe_pairs": [list(key) for key in sorted(expected - set(grouped))],
              "probe_failures": failures, "contrasts": contrasts, "pairs": pairs,
              "candidates": list(candidate_pairs.values()), "costs": costs,
              "reference_tests": [{"case": r["case"], "variant": r["variant"], "target": r["target"],
                                   "returncode": r["returncode"], "timed_out": r["timed_out"]}
                                  for r in records if r["kind"] == "reference_test"],
              "scope": "Two exposed bugs, repeated probes; no independent repair utility labels or model comparison"}
    path = output / "analysis.json"
    if path.exists():
        raise ValueError("Analysis already exists; preserve original")
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"contrasts": contrasts, "candidates": [
        {"id": r["candidate"]["id"], "attribute": r["candidate"]["attribute"],
         "comparable_pairs": r["comparable_pairs"], "different_pairs": r["different_pairs"],
         "unavailable_pairs": r["unavailable_pairs"]} for r in result["candidates"]],
         "costs": costs}, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="run-001")
    analyze(parser.parse_args().name)
